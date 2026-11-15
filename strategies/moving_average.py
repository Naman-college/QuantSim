"""
moving_average.py - Strategy 5: Dual Moving Average Crossover.
Maintained by Member 3 (Strategy Developer).

Academic Concepts Showcased:
- pandas rolling window calculations: df['Close'].rolling(window).mean()
- Vectorized conditional signal generation with np.where()
- Eliminating lookahead bias using .shift(1)
- Golden Cross (Fast crosses above Slow) & Death Cross (Fast crosses below Slow)
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
from strategies.base import BaseStrategy
from core.metrics import calculate_metrics, calculate_drawdown_series


class MovingAverageCrossoverStrategy(BaseStrategy):
    name = "5. Moving Average Crossover"
    description = "Buys on Golden Cross (Fast SMA crosses above Slow SMA) and exits to cash on Death Cross."

    def run(
        self,
        df: pd.DataFrame,
        initial_capital: float = 10000.0,
        fast_period: int = 20,
        slow_period: int = 50,
        ma_type: str = "SMA",
        use_trend_filter: bool = False,
        trend_filter_period: int = 200,
        stop_loss_pct: float = 0.0,
        transaction_fee_pct: float = 0.1,
        **params
    ) -> Dict[str, Any]:
        """
        Parameters:
            fast_period (int): Lookback for fast MA (e.g. 20 days)
            slow_period (int): Lookback for slow MA (e.g. 50 days)
            ma_type (str): "SMA" (Simple) or "EMA" (Exponential)
            use_trend_filter (bool): If True, only enters long when price > Trend MA (e.g. 200 SMA)
            trend_filter_period (int): Period for macroeconomic trend filter (e.g. 200 days)
            stop_loss_pct (float): Hard stop-loss % to exit before Death Cross (0.0 = disabled)
            transaction_fee_pct (float): Brokerage/fee % applied per trade entry & exit
        """
        if fast_period >= slow_period:
            raise ValueError(f"Fast period ({fast_period}) must be strictly less than Slow period ({slow_period}).")

        res = df.copy()
        res['Market_Return'] = res['Close'].pct_change().fillna(0.0)

        # 1. Calculate Moving Averages based on type
        ma_label = "EMA" if ma_type.upper() == "EMA" else "SMA"
        if ma_label == "EMA":
            res['MA_Fast'] = res['Close'].ewm(span=int(fast_period), adjust=False).mean()
            res['MA_Slow'] = res['Close'].ewm(span=int(slow_period), adjust=False).mean()
        else:
            res['MA_Fast'] = res['Close'].rolling(window=int(fast_period), min_periods=1).mean()
            res['MA_Slow'] = res['Close'].rolling(window=int(slow_period), min_periods=1).mean()

        # Trend filter (e.g. 200 SMA)
        if use_trend_filter:
            res['MA_Trend'] = res['Close'].rolling(window=int(trend_filter_period), min_periods=1).mean()

        # 2. Sequential simulation to handle Stop-Loss and Trade Fees
        n = len(res)
        signal = np.zeros(n, dtype=int)
        closes = res['Close'].values
        dates = res.index
        fast_vals = res['MA_Fast'].values
        slow_vals = res['MA_Slow'].values
        trend_vals = res['MA_Trend'].values if use_trend_filter else None

        trade_events = []
        in_pos = False
        entry_price = 0.0
        fee_ratio = max(0.0, float(transaction_fee_pct)) / 100.0
        fee_penalties = np.zeros(n, dtype=float)
        sl_mult = 1.0 - (abs(stop_loss_pct) / 100.0) if stop_loss_pct > 0 else float('-inf')

        for i in range(n):
            curr_price = closes[i]
            bullish_cross = fast_vals[i] > slow_vals[i]
            if use_trend_filter and trend_vals is not None:
                bullish_cross = bullish_cross and (curr_price > trend_vals[i])

            if not in_pos:
                if bullish_cross:
                    in_pos = True
                    entry_price = curr_price
                    signal[i] = 1
                    fee_penalties[i] += fee_ratio
                    label = f"BUY (Golden Cross {ma_label})"
                    trade_events.append((dates[i], curr_price, label))
                else:
                    signal[i] = 0
            else:
                pct_change = ((curr_price - entry_price) / entry_price) * 100.0
                
                # Check exit conditions: Death cross OR stop loss
                if stop_loss_pct > 0 and curr_price <= entry_price * sl_mult:
                    # Stop loss triggered
                    in_pos = False
                    signal[i] = 0
                    fee_penalties[i] += fee_ratio
                    trade_events.append((dates[i], curr_price, f"SELL (Stop Loss {pct_change:.1f}%)"))
                elif not bullish_cross:
                    # Death Cross exit
                    in_pos = False
                    signal[i] = 0
                    fee_penalties[i] += fee_ratio
                    trade_events.append((dates[i], curr_price, f"SELL (Death Cross {pct_change:+.1f}%)"))
                else:
                    signal[i] = 1

        res['Signal'] = signal

        # 3. Strategy Return (shift(1) prevents lookahead bias) minus trade fees
        gross_return = res['Signal'].shift(1).fillna(0) * res['Market_Return']
        res['Strategy_Return'] = gross_return - fee_penalties

        # 4. Cumulative Equity Curve
        res['Equity'] = initial_capital * (1.0 + res['Strategy_Return']).cumprod()

        # 5. Underwater Drawdown
        res['Drawdown'] = calculate_drawdown_series(res['Equity'])

        metrics = calculate_metrics(res['Equity'], res['Strategy_Return'], initial_capital)
        metrics["Total Trades"] = len([e for e in trade_events if "BUY" in e[2]])

        return {
            "df": res,
            "metrics": metrics,
            "trade_events": trade_events,
            "params": {
                "MA Model": f"{fast_period}/{slow_period} {ma_label}",
                "Fast Window": f"{fast_period} days",
                "Slow Window": f"{slow_period} days",
                "Trend Filter": f">{trend_filter_period} SMA" if use_trend_filter else "Off",
                "Stop Loss": f"-{stop_loss_pct:.1f}%" if stop_loss_pct > 0 else "Off",
                "Fee / Trade": f"{transaction_fee_pct:.2f}%"
            }
        }

