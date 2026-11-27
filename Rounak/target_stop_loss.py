"""
Rounak/target_stop_loss.py - Strategy 4: Target Gain & Stop Loss (Risk-Managed Trading).
Member: Rounak (Code for the Strategies).

Academic Concepts Showcased:
- State-machine simulation tracking open/closed positions and entry price anchors
- Take-Profit targets, hard Stop-Losses, optional Trailing Stops, and Max-Hold timeouts
- Cooldown periods and per-trade transaction fee deductions
"""

import pandas as pd  # DataFrame handling
import numpy as np  # NumPy arrays for fast sequential simulation
from typing import Dict, Any  # Return type annotations
from Rounak.base import BaseStrategy  # Base class contract
from Naman.metrics import calculate_metrics, calculate_drawdown_series  # Shared KPI & drawdown calculators


class TargetStopLossStrategy(BaseStrategy):
    name = "4. Target Gain & Stop Loss"  # Strategy registry name
    description = "Buys the stock and automatically exits when reaching a target profit % or stop-loss %."

    def run(
        self,
        df: pd.DataFrame,
        initial_capital: float = 10000.0,
        target_gain_pct: float = 5.0,
        stop_loss_pct: float = 3.0,
        trailing_stop: bool = False,
        trailing_stop_pct: float = 3.0,
        max_hold_days: int = 0,
        re_entry_wait_days: int = 1,
        transaction_fee_pct: float = 0.1,
        **params
    ) -> Dict[str, Any]:
        """
        Executes a state-machine trade loop with take-profit, stop-loss, trailing stop, and cooldown rules.

        Parameters:
            target_gain_pct (float): Exit with profit when price rises by this % above entry
            stop_loss_pct (float): Exit with loss when price falls by this % below entry
            trailing_stop (bool): If True, raises stop threshold dynamically as price makes new highs
            trailing_stop_pct (float): % pullback from peak trade price that triggers trailing stop
            max_hold_days (int): Force exit after N days if neither target nor stop hit (0 = disabled)
            re_entry_wait_days (int): Cooldown days spent in cash before re-entering after an exit
            transaction_fee_pct (float): Brokerage fee % subtracted on every BUY and SELL event
        """
        res = df.copy()  # Copy input DataFrame
        res['Market_Return'] = res['Close'].pct_change().fillna(0.0)  # Daily asset percentage return

        n = len(res)  # Total number of trading bars
        signal = np.zeros(n, dtype=int)  # Position state array (0 = cash, 1 = in trade)
        closes = res['Close'].values  # Fast NumPy view of closing prices
        dates = res.index  # Trading timestamps

        trade_events = []  # List of (date, price, action_str) markers
        in_position = False  # Current state: whether a trade is open
        entry_price = 0.0  # Closing price at which current trade was opened
        peak_price = 0.0  # Highest closing price observed since opening current trade
        days_in_trade = 0  # Holding duration counter for max_hold_days check
        cooldown = 0  # Remaining wait days before next BUY is permitted
        total_wins = 0  # Count of winning exits
        total_losses = 0  # Count of losing exits
        fee_ratio = max(0.0, float(transaction_fee_pct)) / 100.0  # Convert fee % into decimal penalty
        fee_penalties = np.zeros(n, dtype=float)  # Per-day brokerage fee drag applied to returns

        target_multiplier = 1.0 + (target_gain_pct / 100.0) if target_gain_pct > 0 else float('inf')  # Price ratio for take-profit
        stop_multiplier = 1.0 - (stop_loss_pct / 100.0) if stop_loss_pct > 0 else float('-inf')  # Price ratio for stop-loss

        for i in range(n):  # Step through market history bar by bar
            curr_price = closes[i]  # Today's closing price

            if not in_position:  # State 1: Currently in Cash
                if cooldown <= 0:  # Enter immediately once cooldown expires
                    in_position = True  # Transition to In-Position state
                    entry_price = curr_price  # Anchor entry price for target/stop math
                    peak_price = curr_price  # Initialize peak price for trailing stop
                    days_in_trade = 0  # Reset holding day counter
                    signal[i] = 1  # Mark day i as holding stock
                    fee_penalties[i] += fee_ratio  # Charge entry transaction fee
                    trade_events.append((dates[i], curr_price, "BUY"))  # Log BUY event
                else:
                    signal[i] = 0  # Remain in cash during cooldown
                    cooldown -= 1  # Tick down remaining cooldown days
            else:  # State 2: Currently holding an open position
                days_in_trade += 1  # Increment days held
                peak_price = max(peak_price, curr_price)  # Update highest price reached during this trade
                pct_change_from_entry = (curr_price - entry_price) / entry_price  # Current trade's unrealized return

                trailing_hit = False  # Check whether optional trailing stop triggered today
                if trailing_stop and trailing_stop_pct > 0:  # Only evaluate if trailing stop is enabled
                    trail_threshold = peak_price * (1.0 - (trailing_stop_pct / 100.0))  # Ratcheted stop level below peak
                    if curr_price <= trail_threshold and curr_price < peak_price:  # Price pulled back past trailing threshold
                        trailing_hit = True  # Flag trailing exit

                if curr_price >= entry_price * target_multiplier:  # Priority 1: Take-Profit target reached
                    in_position = False  # Exit to cash
                    signal[i] = 0  # Update position signal
                    cooldown = re_entry_wait_days  # Start post-exit cooldown
                    total_wins += 1  # Count as winning trade
                    fee_penalties[i] += fee_ratio  # Charge exit fee
                    trade_events.append((dates[i], curr_price, f"SELL (Gain +{pct_change_from_entry*100:.1f}%)"))  # Log gain exit

                elif trailing_hit:  # Priority 2: Trailing Stop triggered
                    in_position = False  # Exit to cash
                    signal[i] = 0
                    cooldown = re_entry_wait_days
                    if pct_change_from_entry >= 0:  # Classify trailing exit as win or loss based on net gain
                        total_wins += 1
                    else:
                        total_losses += 1
                    fee_penalties[i] += fee_ratio
                    trade_events.append((dates[i], curr_price, f"SELL (Trailing Stop {pct_change_from_entry*100:+.1f}%)"))

                elif curr_price <= entry_price * stop_multiplier:  # Priority 3: Hard Stop-Loss hit
                    in_position = False  # Cut loss and exit to cash
                    signal[i] = 0
                    cooldown = re_entry_wait_days
                    total_losses += 1  # Count as losing trade
                    fee_penalties[i] += fee_ratio
                    trade_events.append((dates[i], curr_price, f"SELL (Loss {pct_change_from_entry*100:.1f}%)"))

                elif max_hold_days > 0 and days_in_trade >= max_hold_days:  # Priority 4: Max holding period timeout
                    in_position = False  # Close stagnant trade
                    signal[i] = 0
                    cooldown = re_entry_wait_days
                    if pct_change_from_entry >= 0:  # Record outcome
                        total_wins += 1
                    else:
                        total_losses += 1
                    fee_penalties[i] += fee_ratio
                    trade_events.append((dates[i], curr_price, f"SELL (Timeout {days_in_trade}d: {pct_change_from_entry*100:+.1f}%)"))

                else:  # No exit condition met: stay invested
                    signal[i] = 1  # Hold position

        res['Signal'] = signal  # Store position signal series

        # Shift signal by 1 day to avoid lookahead bias, then subtract entry/exit brokerage fees
        gross_return = res['Signal'].shift(1).fillna(0) * res['Market_Return']
        res['Strategy_Return'] = gross_return - fee_penalties  # Net daily strategy return

        res['Equity'] = initial_capital * (1.0 + res['Strategy_Return']).cumprod()  # Compound equity curve
        res['Drawdown'] = calculate_drawdown_series(res['Equity'])  # Underwater drawdown %

        metrics = calculate_metrics(res['Equity'], res['Strategy_Return'], initial_capital)  # Standard financial KPIs
        metrics["Take-Profit Exits"] = total_wins  # Append win count metric
        metrics["Stop-Loss Exits"] = total_losses  # Append loss count metric
        metrics["Total Trades"] = total_wins + total_losses  # Total completed round-trip trades

        return {  # Standardized output dictionary
            "df": res,
            "metrics": metrics,
            "trade_events": trade_events,
            "params": {
                "Target Gain": f"+{target_gain_pct:.1f}%",
                "Stop Loss": f"-{stop_loss_pct:.1f}%",
                "Trailing Stop": f"{trailing_stop_pct:.1f}%" if trailing_stop else "Off",
                "Max Hold Days": f"{max_hold_days} days" if max_hold_days > 0 else "Off",
                "Cooldown": f"{re_entry_wait_days} day{'s' if re_entry_wait_days > 1 else ''}",
                "Fee / Trade": f"{transaction_fee_pct:.2f}%"
            }
        }
