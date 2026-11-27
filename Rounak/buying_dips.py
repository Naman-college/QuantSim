"""
Rounak/buying_dips.py - Strategy 2: Buying Dips (Pullback / Mean-Reversion Strategy).
Member: Rounak (Code for the Strategies).

Academic Concepts Showcased:
- Multi-day or single-day pullback detection via pct_change(periods=dip_window)
- Holding window simulation with optional Take-Profit, Stop-Loss, and transaction fees
- Eliminating lookahead bias with .shift(1) before multiplying by next-day returns
"""

import pandas as pd  # DataFrame handling
import numpy as np  # Fast array allocation
from typing import Dict, Any  # Type annotations
from Rounak.base import BaseStrategy  # Abstract strategy base class
from Naman.metrics import calculate_metrics, calculate_drawdown_series  # Shared KPI & drawdown helpers


class BuyingDipsStrategy(BaseStrategy):
    name = "2. Buying Dips"  # Strategy identifier shown in UI & leaderboard
    description = "Enters the market whenever price drops by a specified % (buying the dip) and holds for N days."

    def run(
        self,
        df: pd.DataFrame,
        initial_capital: float = 10000.0,
        dip_pct: float = 2.0,
        dip_window: int = 1,
        hold_days: int = 10,
        take_profit_pct: float = 0.0,
        stop_loss_pct: float = 0.0,
        transaction_fee_pct: float = 0.1,
        **params
    ) -> Dict[str, Any]:
        """
        Buys after a pullback of `dip_pct`% over `dip_window` days and holds up to `hold_days`
        (with optional early Take-Profit / Stop-Loss exits and brokerage fees).

        Parameters:
            dip_pct (float): Percentage drop threshold to trigger a buy (e.g. 2.0%)
            dip_window (int): Lookback window in trading days to measure the drop (default 1 day)
            hold_days (int): Maximum days to hold after a dip entry (default 10 days)
            take_profit_pct (float): Optional profit target % to exit early (0.0 = disabled)
            stop_loss_pct (float): Optional stop-loss % to cut losses early (0.0 = disabled)
            transaction_fee_pct (float): Brokerage fee % applied per BUY and SELL
        """
        res = df.copy()  # Work on a copy to keep original price DataFrame untouched
        res['Market_Return'] = res['Close'].pct_change().fillna(0.0)  # Single-day percentage return

        win = max(1, int(dip_window))  # Ensure lookback window is at least 1 day
        hold = max(1, int(hold_days))  # Ensure holding period is at least 1 day
        window_ret = res['Close'].pct_change(periods=win).fillna(0.0)  # N-day cumulative drop from win days ago
        dip_threshold = -(abs(float(dip_pct)) / 100.0)  # Convert positive dip % into negative decimal threshold
        is_dip = window_ret <= dip_threshold  # True on days where pullback meets or exceeds threshold

        n = len(res)  # Total number of trading bars
        signal = np.zeros(n, dtype=int)  # Position array (0 = cash, 1 = invested)
        closes = res['Close'].values  # Fast NumPy view of closing prices
        dates = res.index  # Trading timestamps
        fee_ratio = max(0.0, float(transaction_fee_pct)) / 100.0  # Convert fee % to decimal
        fee_penalties = np.zeros(n, dtype=float)  # Daily brokerage fee drag

        tp_mult = 1.0 + (take_profit_pct / 100.0) if take_profit_pct > 0 else float('inf')  # Take-profit price ratio
        sl_mult = 1.0 - (stop_loss_pct / 100.0) if stop_loss_pct > 0 else float('-inf')  # Stop-loss price ratio

        trade_events = []  # Chronological BUY/SELL markers
        in_pos = False  # Current open-position flag
        entry_price = 0.0  # Entry price anchor for take-profit / stop-loss
        days_left = 0  # Countdown timer for holding window

        for i in range(n):  # Step sequentially through trading history
            curr_price = float(closes[i])  # Today's closing price

            if not in_pos:  # Currently in cash
                if is_dip.iloc[i]:  # Qualifying dip detected today
                    in_pos = True  # Enter long position
                    entry_price = curr_price  # Anchor entry price
                    days_left = hold - 1  # Count today as day 1 of holding window
                    signal[i] = 1  # Mark position active
                    fee_penalties[i] += fee_ratio  # Charge entry fee
                    trade_events.append((dates[i], curr_price, f"BUY (Dip {window_ret.iloc[i]*100:.1f}%)"))  # Record BUY marker
                else:
                    signal[i] = 0  # Stay in cash
            else:  # Currently holding a dip trade
                pct_change = ((curr_price - entry_price) / entry_price) * 100.0  # Current trade return %

                if take_profit_pct > 0 and curr_price >= entry_price * tp_mult:  # Early Take-Profit exit
                    in_pos = False
                    signal[i] = 0
                    days_left = 0
                    fee_penalties[i] += fee_ratio
                    trade_events.append((dates[i], curr_price, f"SELL (Gain +{pct_change:.1f}%)"))
                elif stop_loss_pct > 0 and curr_price <= entry_price * sl_mult:  # Early Stop-Loss exit
                    in_pos = False
                    signal[i] = 0
                    days_left = 0
                    fee_penalties[i] += fee_ratio
                    trade_events.append((dates[i], curr_price, f"SELL (Stop {pct_change:.1f}%)"))
                elif is_dip.iloc[i]:  # Another qualifying dip resets holding window while already invested
                    days_left = hold - 1
                    signal[i] = 1
                elif days_left > 0:  # Continue holding within window
                    days_left -= 1
                    signal[i] = 1
                else:  # Holding window expired -> exit to cash
                    in_pos = False
                    signal[i] = 0
                    fee_penalties[i] += fee_ratio
                    trade_events.append((dates[i], curr_price, f"SELL (Hold End {pct_change:+.1f}%)"))

        res['Signal'] = signal  # Store position signal column

        # Shift signal by 1 day to avoid lookahead bias, then subtract transaction fees
        gross_return = res['Signal'].shift(1).fillna(0) * res['Market_Return']
        res['Strategy_Return'] = gross_return - fee_penalties  # Net daily strategy return

        res['Equity'] = initial_capital * (1.0 + res['Strategy_Return']).cumprod()  # Compounded portfolio equity
        res['Drawdown'] = calculate_drawdown_series(res['Equity'])  # Underwater % drawdown curve

        metrics = calculate_metrics(res['Equity'], res['Strategy_Return'], initial_capital)  # Standard financial KPIs
        metrics["Total Trades"] = len([e for e in trade_events if "BUY" in e[2]])  # Count total dip entries

        return {  # Standardized strategy result packet
            "df": res,
            "metrics": metrics,
            "trade_events": trade_events,
            "params": {
                "Dip Trigger": f"-{dip_pct:.1f}%",
                "Lookback Window": f"{win} days" if win > 1 else "1 day",
                "Holding Window": f"{hold} days",
                "Take Profit": f"+{take_profit_pct:.1f}%" if take_profit_pct > 0 else "Off",
                "Stop Loss": f"-{stop_loss_pct:.1f}%" if stop_loss_pct > 0 else "Off",
                "Fee / Trade": f"{transaction_fee_pct:.2f}%",
            }
        }
