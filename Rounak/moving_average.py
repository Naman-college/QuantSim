"""
Rounak/moving_average.py - Strategy 5: Dual Moving Average Crossover (Trend Following).
Member: Rounak (Code for the Strategies).

Academic Concepts Showcased:
- Simple Moving Average (rolling().mean()) vs Exponential Moving Average (ewm().mean())
- Golden Cross (Fast MA > Slow MA) & Death Cross (Fast MA < Slow MA)
- Optional macro Trend Filter (Price > 200 SMA) and hard Stop-Loss protection
"""

import pandas as pd  # DataFrame rolling and exponential moving average calculations
import numpy as np  # NumPy signal and fee arrays
from typing import Dict, Any  # Return type annotations
from Rounak.base import BaseStrategy  # Abstract strategy interface
from Naman.metrics import calculate_metrics, calculate_drawdown_series  # Shared KPI & drawdown calculator


class MovingAverageCrossoverStrategy(BaseStrategy):
    name = "5. Moving Average Crossover"  # Strategy display name
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
        Simulates a dual moving average crossover system with optional trend filter & stop-loss.

        Parameters:
            fast_period (int): Short lookback window (e.g. 20 days)
            slow_period (int): Long lookback window (e.g. 50 days; must be > fast_period)
            ma_type (str): "SMA" (Simple Moving Average) or "EMA" (Exponential Moving Average)
            use_trend_filter (bool): If True, requires Price > trend_filter_period SMA to buy
            trend_filter_period (int): Lookback for long-term trend filter (default 200 days)
            stop_loss_pct (float): Optional hard stop-loss % (0.0 disables stop-loss)
            transaction_fee_pct (float): Brokerage fee % applied per BUY and SELL
        """
        if fast_period >= slow_period:  # Validate that fast window is strictly shorter than slow window
            raise ValueError(f"Fast period ({fast_period}) must be strictly less than Slow period ({slow_period}).")

        res = df.copy()  # Clone input DataFrame
        res['Market_Return'] = res['Close'].pct_change().fillna(0.0)  # Compute daily asset return

        ma_label = "EMA" if ma_type.upper() == "EMA" else "SMA"  # Normalize MA type string
        if ma_label == "EMA":  # Exponential Moving Average places higher weight on recent prices
            res['MA_Fast'] = res['Close'].ewm(span=int(fast_period), adjust=False).mean()  # Fast EMA
            res['MA_Slow'] = res['Close'].ewm(span=int(slow_period), adjust=False).mean()  # Slow EMA
        else:  # Simple Moving Average weights all days in window equally
            res['MA_Fast'] = res['Close'].rolling(window=int(fast_period), min_periods=1).mean()  # Fast SMA
            res['MA_Slow'] = res['Close'].rolling(window=int(slow_period), min_periods=1).mean()  # Slow SMA

        if use_trend_filter:  # Compute optional long-term 200-day SMA regime filter
            res['MA_Trend'] = res['Close'].rolling(window=int(trend_filter_period), min_periods=1).mean()

        n = len(res)  # Total number of trading days
        signal = np.zeros(n, dtype=int)  # Daily position signal (0 = cash, 1 = invested)
        closes = res['Close'].values  # Closing prices array
        dates = res.index  # Date index
        fast_vals = res['MA_Fast'].values  # Fast MA values array
        slow_vals = res['MA_Slow'].values  # Slow MA values array
        trend_vals = res['MA_Trend'].values if use_trend_filter else None  # Optional trend filter array

        trade_events = []  # List of BUY/SELL markers
        in_pos = False  # Tracks open position state
        entry_price = 0.0  # Price when position was entered (for stop-loss & trade % logging)
        fee_ratio = max(0.0, float(transaction_fee_pct)) / 100.0  # Convert % fee into decimal
        fee_penalties = np.zeros(n, dtype=float)  # Fee penalty array subtracted on trade days
        sl_mult = 1.0 - (abs(stop_loss_pct) / 100.0) if stop_loss_pct > 0 else float('-inf')  # Stop-loss price multiplier

        for i in range(n):  # Simulate crossover & stop-loss logic day by day
            curr_price = closes[i]  # Today's closing price
            bullish_cross = fast_vals[i] > slow_vals[i]  # Golden Cross condition: Fast MA above Slow MA
            if use_trend_filter and trend_vals is not None:  # Require price above macro trend SMA if enabled
                bullish_cross = bullish_cross and (curr_price > trend_vals[i])

            if not in_pos:  # Currently flat (in cash)
                if bullish_cross:  # Enter on Golden Cross
                    in_pos = True  # Open long position
                    entry_price = curr_price  # Save entry price
                    signal[i] = 1  # Set active signal
                    fee_penalties[i] += fee_ratio  # Deduct entry fee
                    label = f"BUY (Golden Cross {ma_label})"  # Descriptive marker label
                    trade_events.append((dates[i], curr_price, label))  # Log BUY event
                else:
                    signal[i] = 0  # Stay in cash
            else:  # Currently holding long position
                pct_change = ((curr_price - entry_price) / entry_price) * 100.0  # Unrealized trade P&L %

                if stop_loss_pct > 0 and curr_price <= entry_price * sl_mult:  # Exit early if stop-loss breached
                    in_pos = False  # Close position
                    signal[i] = 0  # Flat signal
                    fee_penalties[i] += fee_ratio  # Deduct exit fee
                    trade_events.append((dates[i], curr_price, f"SELL (Stop Loss {pct_change:.1f}%)"))  # Log stop-loss exit
                elif not bullish_cross:  # Death Cross: Fast MA fell below Slow MA (or broke trend filter)
                    in_pos = False  # Exit to cash
                    signal[i] = 0  # Flat signal
                    fee_penalties[i] += fee_ratio  # Deduct exit fee
                    trade_events.append((dates[i], curr_price, f"SELL (Death Cross {pct_change:+.1f}%)"))  # Log Death Cross exit
                else:
                    signal[i] = 1  # Continue holding trend

        res['Signal'] = signal  # Store position signal

        # Shift signal by 1 day so signals generated at Day t Close only earn Day t+1 Market_Return
        gross_return = res['Signal'].shift(1).fillna(0) * res['Market_Return']
        res['Strategy_Return'] = gross_return - fee_penalties  # Net daily strategy return after fees

        res['Equity'] = initial_capital * (1.0 + res['Strategy_Return']).cumprod()  # Compounded portfolio equity
        res['Drawdown'] = calculate_drawdown_series(res['Equity'])  # Underwater drawdown % curve

        metrics = calculate_metrics(res['Equity'], res['Strategy_Return'], initial_capital)  # Calculate financial KPIs
        metrics["Total Trades"] = len([e for e in trade_events if "BUY" in e[2]])  # Count total trade entries

        return {  # Standardized strategy result packet
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
