"""
buying_dips.py - Strategy 2: Buying Dips.
Maintained by Member 3 (Strategy Developer).

Academic Concepts Showcased:
- Detecting market pullbacks using pct_change()
- Vectorized holding window simulation
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
from strategies.base import BaseStrategy
from core.metrics import calculate_metrics, calculate_drawdown_series


class BuyingDipsStrategy(BaseStrategy):
    name = "2. Buying Dips"
    description = "Enters the market whenever price drops by a specified % (buying the dip) and holds for 10 days."

    def run(self, df: pd.DataFrame, initial_capital: float = 10000.0, dip_pct: float = 2.0, **params) -> Dict[str, Any]:
        """
        Parameters:
            dip_pct (float): Single-day percentage drop to trigger buy (e.g. 2.0%)
        """
        res = df.copy()
        res['Market_Return'] = res['Close'].pct_change().fillna(0.0)

        # 1. Identify "Dip" days where price fell by at least dip_pct %
        dip_threshold = -(abs(dip_pct) / 100.0)
        is_dip = res['Market_Return'] <= dip_threshold

        # 2. When a dip occurs, hold for 10 days
        hold_days = 10
        signal = np.zeros(len(res), dtype=int)
        days_left = 0

        for i in range(len(res)):
            if is_dip.iloc[i]:
                days_left = hold_days
            if days_left > 0:
                signal[i] = 1
                days_left -= 1
            else:
                signal[i] = 0

        res['Signal'] = signal

        # 3. Strategy Return (shift(1) avoids lookahead bias)
        res['Strategy_Return'] = res['Signal'].shift(1).fillna(0) * res['Market_Return']

        # 4. Cumulative Equity
        res['Equity'] = initial_capital * (1.0 + res['Strategy_Return']).cumprod()
        res['Drawdown'] = calculate_drawdown_series(res['Equity'])

        trade_events = self.extract_trade_events(res)
        metrics = calculate_metrics(res['Equity'], res['Strategy_Return'], initial_capital)

        return {
            "df": res,
            "metrics": metrics,
            "trade_events": trade_events,
            "params": {"Dip Trigger": f"-{dip_pct}%", "Holding Window": "10 days"}
        }
