"""
target_stop_loss.py - Strategy 4: Target Gain & Stop Loss.
Maintained by Member 3 (Strategy Developer).

Academic Concepts Showcased:
- Trade risk management (Fixed Profit Target vs Fixed Stop Loss)
- Position state tracking and entry price anchoring
- Win/loss trade ratio calculation
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
from strategies.base import BaseStrategy
from core.metrics import calculate_metrics, calculate_drawdown_series


class TargetStopLossStrategy(BaseStrategy):
    name = "4. Target Gain & Stop Loss"
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
        Parameters:
            target_gain_pct (float): Exit when trade is up by this % (e.g. 5.0%)
            stop_loss_pct (float): Exit when trade is down by this % (e.g. 3.0%)
            trailing_stop (bool): If True, stop price ratchets up as price hits new highs
            trailing_stop_pct (float): Distance below the peak price to trigger trailing stop (e.g. 3.0%)
            max_hold_days (int): Exit after N days if neither target nor stop hit (0 = off)
            re_entry_wait_days (int): Days to wait in cash before opening the next trade (e.g. 1)
            transaction_fee_pct (float): Brokerage/fee % applied per trade entry & exit
        """
        res = df.copy()
        res['Market_Return'] = res['Close'].pct_change().fillna(0.0)

        n = len(res)
        signal = np.zeros(n, dtype=int)
        closes = res['Close'].values
        dates = res.index

        trade_events = []
        in_position = False
        entry_price = 0.0
        peak_price = 0.0
        days_in_trade = 0
        cooldown = 0
        total_wins = 0
        total_losses = 0
        fee_ratio = max(0.0, float(transaction_fee_pct)) / 100.0
        fee_penalties = np.zeros(n, dtype=float)

        target_multiplier = 1.0 + (target_gain_pct / 100.0) if target_gain_pct > 0 else float('inf')
        stop_multiplier = 1.0 - (stop_loss_pct / 100.0) if stop_loss_pct > 0 else float('-inf')

        for i in range(n):
            curr_price = closes[i]

            if not in_position:
                if cooldown <= 0:
                    # Enter new position
                    in_position = True
                    entry_price = curr_price
                    peak_price = curr_price
                    days_in_trade = 0
                    signal[i] = 1
                    fee_penalties[i] += fee_ratio
                    trade_events.append((dates[i], curr_price, "BUY"))
                else:
                    signal[i] = 0
                    cooldown -= 1
            else:
                days_in_trade += 1
                peak_price = max(peak_price, curr_price)
                pct_change_from_entry = (curr_price - entry_price) / entry_price

                # Check trailing stop condition
                trailing_hit = False
                if trailing_stop and trailing_stop_pct > 0:
                    trail_threshold = peak_price * (1.0 - (trailing_stop_pct / 100.0))
                    if curr_price <= trail_threshold and curr_price < peak_price:
                        trailing_hit = True

                if curr_price >= entry_price * target_multiplier:
                    # Target gain hit (Take Profit)
                    in_position = False
                    signal[i] = 0
                    cooldown = re_entry_wait_days
                    total_wins += 1
                    fee_penalties[i] += fee_ratio
                    trade_events.append((dates[i], curr_price, f"SELL (Gain +{pct_change_from_entry*100:.1f}%)"))

                elif trailing_hit:
                    # Trailing stop hit
                    in_position = False
                    signal[i] = 0
                    cooldown = re_entry_wait_days
                    if pct_change_from_entry >= 0:
                        total_wins += 1
                    else:
                        total_losses += 1
                    fee_penalties[i] += fee_ratio
                    trade_events.append((dates[i], curr_price, f"SELL (Trailing Stop {pct_change_from_entry*100:+.1f}%)"))

                elif curr_price <= entry_price * stop_multiplier:
                    # Stop loss hit (Cut Loss)
                    in_position = False
                    signal[i] = 0
                    cooldown = re_entry_wait_days
                    total_losses += 1
                    fee_penalties[i] += fee_ratio
                    trade_events.append((dates[i], curr_price, f"SELL (Loss {pct_change_from_entry*100:.1f}%)"))

                elif max_hold_days > 0 and days_in_trade >= max_hold_days:
                    # Time limit reached
                    in_position = False
                    signal[i] = 0
                    cooldown = re_entry_wait_days
                    if pct_change_from_entry >= 0:
                        total_wins += 1
                    else:
                        total_losses += 1
                    fee_penalties[i] += fee_ratio
                    trade_events.append((dates[i], curr_price, f"SELL (Timeout {days_in_trade}d: {pct_change_from_entry*100:+.1f}%)"))

                else:
                    # Still in position
                    signal[i] = 1

        res['Signal'] = signal

        # Strategy daily return (shifted by 1 to prevent lookahead bias) minus trade fees
        gross_return = res['Signal'].shift(1).fillna(0) * res['Market_Return']
        res['Strategy_Return'] = gross_return - fee_penalties

        # Cumulative equity
        res['Equity'] = initial_capital * (1.0 + res['Strategy_Return']).cumprod()
        res['Drawdown'] = calculate_drawdown_series(res['Equity'])

        metrics = calculate_metrics(res['Equity'], res['Strategy_Return'], initial_capital)
        metrics["Take-Profit Exits"] = total_wins
        metrics["Stop-Loss Exits"] = total_losses
        metrics["Total Trades"] = total_wins + total_losses

        return {
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

