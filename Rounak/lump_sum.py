"""
Rounak/lump_sum.py - Strategy 1: Lump Sum Investment (Buy & Hold Benchmark).
Member: Rounak (Code for the Strategies).

Academic Concepts Showcased:
- Vectorized daily percentage returns via df['Close'].pct_change()
- Compound wealth growth using (1 + returns).cumprod()
- Capital split between equity allocation and interest-bearing cash reserve
"""

import pandas as pd  # DataFrame manipulation
import numpy as np  # Vectorized array math for cash compounding
from typing import Dict, Any  # Return type hints
from Rounak.base import BaseStrategy  # Abstract strategy interface
from Naman.metrics import calculate_metrics, calculate_drawdown_series  # Shared KPI & drawdown calculator


class LumpSumStrategy(BaseStrategy):
    name = "1. Lump Sum Investment"  # Display name used in UI & strategy registry
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
        Simulates Day-1 Lump Sum investment with optional partial cash reserve and transaction fee.

        Parameters:
            initial_capital (float): Total starting cash balance
            allocation_pct (float): % of capital invested into equity on Day 1 (0 to 100)
            cash_interest_rate_pct (float): Annual % yield earned on unallocated cash (e.g. 4.0% p.a.)
            transaction_fee_pct (float): One-time brokerage fee % deducted on Day-1 entry
        """
        res = df.copy()  # Copy input OHLCV DataFrame so caller's DataFrame isn't mutated

        res['Market_Return'] = res['Close'].pct_change().fillna(0.0)  # Compute daily close-to-close return; Day 0 = 0.0

        alloc_ratio = max(0.0, min(100.0, float(allocation_pct))) / 100.0  # Clamp equity weight cleanly into [0.0, 1.0]
        fee_ratio = max(0.0, float(transaction_fee_pct)) / 100.0  # Convert fee % (e.g. 0.1) to decimal (0.001)

        invested_capital = initial_capital * alloc_ratio * (1.0 - fee_ratio)  # Capital put into stock after Day-1 brokerage fee
        cash_capital = initial_capital * (1.0 - alloc_ratio)  # Remaining uninvested cash reserve

        # Convert annual interest rate into an equivalent daily compounding rate across 252 trading days
        daily_cash_rate = (1.0 + (cash_interest_rate_pct / 100.0)) ** (1.0 / 252.0) - 1.0 if cash_interest_rate_pct > 0 else 0.0

        stock_equity = invested_capital * (1.0 + res['Market_Return']).cumprod()  # Compound equity sleeve day-by-day
        stock_equity.iloc[0] = invested_capital  # Anchor Day-0 stock value explicitly after fee deduction

        n = len(res)  # Total number of trading days
        cash_growth = np.cumprod(np.full(n, 1.0 + daily_cash_rate))  # Vectorized daily compounding factor for cash reserve
        cash_equity = cash_capital * cash_growth  # Daily value of unallocated cash sleeve

        res['Equity'] = stock_equity + cash_equity  # Total portfolio value = Stock Equity + Cash Reserve
        res['Signal'] = 1 if alloc_ratio > 0 else 0  # Fully invested (1) throughout if any equity was allocated
        res['Strategy_Return'] = res['Equity'].pct_change().fillna(0.0)  # Net daily portfolio percentage return

        res['Drawdown'] = calculate_drawdown_series(res['Equity'])  # Compute underwater peak-to-trough % curve

        first_price = float(res['Close'].iloc[0])  # Entry price on Day 1
        trade_events = []  # List of executed trade markers
        if alloc_ratio > 0:  # Record a single Day-1 BUY event if equity allocation > 0%
            trade_events.append((res.index[0], first_price, f"BUY ({allocation_pct:.0f}% Allocation)"))

        metrics = calculate_metrics(res['Equity'], res['Strategy_Return'], initial_capital)  # Compute Return, CAGR, Sharpe, MDD, Win Rate

        return {  # Standardized strategy output packet
            "df": res,  # Annotated DataFrame with Equity, Signal, Drawdown
            "metrics": metrics,  # Computed KPI dictionary
            "trade_events": trade_events,  # Day-1 BUY marker
            "params": {  # Human-readable parameter summary
                "Initial Capital": f"${initial_capital:,.2f}",
                "Equity Allocation": f"{allocation_pct:.1f}%",
                "Cash Interest Rate": f"{cash_interest_rate_pct:.1f}% p.a.",
                "Transaction Fee": f"{transaction_fee_pct:.2f}%"
            }
        }
