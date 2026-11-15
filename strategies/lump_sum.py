"""
lump_sum.py - Strategy 1: Lump Sum Investment (Buy and Hold).
Maintained by Member 3 (Strategy Developer).

Academic Concepts Showcased:
- Base benchmark comparison
- Vectorized daily percentage returns: df['Close'].pct_change()
- Vectorized cumulative wealth compounding: initial_capital * (1 + returns).cumprod()
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
from strategies.base import BaseStrategy
from core.metrics import calculate_metrics, calculate_drawdown_series


class LumpSumStrategy(BaseStrategy):
    name = "1. Lump Sum Investment"
    description = "Invests entire capital on Day 1 and holds throughout the period (Buy & Hold benchmark)."

    def run(
        self,
        df: pd.DataFrame,
        initial_capital: float = 10000.0,
        allocation_pct: float = 100.0,
        cash_interest_rate_pct: float = 4.0,
        transaction_fee_pct: float = 0.1,
        **params
    ) -> Dict[str, Any]:
        """
        Parameters:
            initial_capital (float): Total starting balance
            allocation_pct (float): % of capital invested into equity (e.g. 100% or 80%)
            cash_interest_rate_pct (float): Annual % yield on unallocated cash reserve (e.g. 4.0% p.a.)
            transaction_fee_pct (float): Brokerage / execution fee % applied on Day 1 (e.g. 0.1%)
        """
        res = df.copy()
        
        # 1. Market daily return
        res['Market_Return'] = res['Close'].pct_change().fillna(0.0)
        
        # 2. Capital distribution
        alloc_ratio = max(0.0, min(100.0, float(allocation_pct))) / 100.0
        fee_ratio = max(0.0, float(transaction_fee_pct)) / 100.0
        
        invested_capital = initial_capital * alloc_ratio * (1.0 - fee_ratio)
        cash_capital = initial_capital * (1.0 - alloc_ratio)
        
        # Daily interest on cash reserve
        daily_cash_rate = (1.0 + (cash_interest_rate_pct / 100.0)) ** (1.0 / 252.0) - 1.0 if cash_interest_rate_pct > 0 else 0.0

        # 3. Daily portfolio simulation
        stock_equity = invested_capital * (1.0 + res['Market_Return']).cumprod()
        # Adjust day 0 stock equity
        stock_equity.iloc[0] = invested_capital

        n = len(res)
        cash_growth = np.cumprod(np.full(n, 1.0 + daily_cash_rate))
        cash_equity = cash_capital * cash_growth
        
        res['Equity'] = stock_equity + cash_equity
        res['Signal'] = 1 if alloc_ratio > 0 else 0
        res['Strategy_Return'] = res['Equity'].pct_change().fillna(0.0)
        
        # 4. Underwater Drawdown
        res['Drawdown'] = calculate_drawdown_series(res['Equity'])
        
        # 5. Trade Events (single buy on day 1 if allocated)
        first_price = float(res['Close'].iloc[0])
        trade_events = []
        if alloc_ratio > 0:
            trade_events.append((res.index[0], first_price, f"BUY ({allocation_pct:.0f}% Allocation)"))
        
        metrics = calculate_metrics(res['Equity'], res['Strategy_Return'], initial_capital)
        
        return {
            "df": res,
            "metrics": metrics,
            "trade_events": trade_events,
            "params": {
                "Initial Capital": f"${initial_capital:,.2f}",
                "Equity Allocation": f"{allocation_pct:.1f}%",
                "Cash Interest Rate": f"{cash_interest_rate_pct:.1f}% p.a.",
                "Transaction Fee": f"{transaction_fee_pct:.2f}%"
            }
        }

