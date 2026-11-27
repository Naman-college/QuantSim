"""
Naman/engine.py - Core Backtest Orchestrator & Cross-Module Coordinator.
Member: Naman (Backend and Bridging Everyone's Work to Complete the Final App).

Bridges:
- Prakshat's Finance API (fetch_stock_data, get_currency_symbol)
- Rounak's Strategies (AVAILABLE_STRATEGIES, LumpSumStrategy benchmark)
- Naman's Backend Metrics (computed inside each strategy run)
"""

from typing import Dict, Any  # Type annotations for structured backtest outputs
from Prakshat.data_manager import fetch_stock_data  # Yahoo Finance + CSV cache loader (Prakshat)
from Prakshat.presets import get_currency_symbol  # Market currency detector (Prakshat)
from Rounak import AVAILABLE_STRATEGIES  # Registry of all 5 trading strategies (Rounak)
from Rounak.lump_sum import LumpSumStrategy  # Buy & Hold benchmark strategy (Rounak)


class BacktestEngine:
    """
    Central backend coordinator executing single-strategy backtests and
    multi-strategy comparative rankings on unified historical price data.
    """

    def __init__(self):
        self.strategies = AVAILABLE_STRATEGIES  # Reference dictionary of all 5 registered strategy instances
        self.benchmark_strategy = LumpSumStrategy()  # Dedicated Lump Sum instance used as baseline benchmark

    def run_backtest(
        self,
        ticker: str,
        strategy_name: str,
        start_date: str = "2020-01-01",
        end_date: str = None,
        initial_capital: float = 10000.0,
        strategy_params: dict = None
    ) -> Dict[str, Any]:
        """
        Executes one selected strategy alongside the Buy & Hold benchmark on a ticker.

        Returns:
            dict with 'ticker', 'currency', 'strategy_name', 'initial_capital',
            'strategy_result', and 'benchmark_result'.
        """
        if strategy_name not in self.strategies:  # Reject unknown strategy names early with clear message
            raise ValueError(f"Unknown strategy '{strategy_name}'. Available: {list(self.strategies.keys())}")

        strategy_params = strategy_params or {}  # Default None params to empty dict for **unpacking

        df = fetch_stock_data(ticker=ticker, start_date=start_date, end_date=end_date)  # Fetch/load cached OHLCV history
        if df.empty or len(df) < 5:  # Ensure sufficient trading bars for meaningful backtest math
            raise ValueError(f"Insufficient historical data points for ticker '{ticker}'.")

        strategy = self.strategies[strategy_name]  # Look up Rounak's selected strategy object
        strat_res = strategy.run(df=df, initial_capital=initial_capital, **strategy_params)  # Simulate chosen strategy

        bench_res = self.benchmark_strategy.run(df=df, initial_capital=initial_capital)  # Run 100% Day-1 Buy & Hold benchmark

        currency = get_currency_symbol(ticker)  # Detect '$' vs 'Rs. ' via Prakshat's preset helper

        return {  # Unified response consumed by Naman/app.py and tests
            "ticker": ticker,
            "currency": currency,
            "strategy_name": strategy_name,
            "initial_capital": float(initial_capital),
            "strategy_result": strat_res,
            "benchmark_result": bench_res,
        }

    def run_all_strategies(
        self,
        ticker: str,
        start_date: str = "2020-01-01",
        end_date: str = None,
        initial_capital: float = 10000.0,
        strategy_params_dict: dict = None
    ) -> Dict[str, Any]:
        """
        Executes all 5 strategies on the exact same historical DataFrame,
        ranks them by Total Return descending, and prepares comparison curves.
        """
        strategy_params_dict = strategy_params_dict or {}  # Default None to empty mapping

        df = fetch_stock_data(ticker=ticker, start_date=start_date, end_date=end_date)  # Load market data once for all 5 strategies
        if df.empty or len(df) < 5:  # Guard against missing or sparse price history
            raise ValueError(f"Insufficient historical data points for ticker '{ticker}'.")

        bench_res = self.benchmark_strategy.run(df=df, initial_capital=initial_capital)  # Compute Buy & Hold baseline

        strategy_results = {}  # Stores full DataFrame + metrics per strategy name
        ranking_table = []  # Stores compact summary rows for leaderboard sorting

        for name, strategy in self.strategies.items():  # Loop across all 5 registered strategies
            params = strategy_params_dict.get(name, {})  # Extract sidebar parameters for this specific strategy
            try:
                res = strategy.run(df=df, initial_capital=initial_capital, **params)  # Run strategy simulation
                strategy_results[name] = res  # Save full result for multi-line chart plotting
                m = res["metrics"]  # Read computed KPI dictionary
                tot_ret = m.get("Total Return (%)", 0.0)  # Total % return
                sharpe = m.get("Sharpe Ratio", 0.0)  # Sharpe ratio
                mdd = m.get("Max Drawdown (%)", 0.0)  # Max drawdown %
                cagr = m.get("CAGR (%)", 0.0)  # Compound annual growth rate %
                final_bal = m.get("Final Balance", initial_capital)  # Ending balance
                trades = len(res.get("trade_events", []))  # Number of recorded trade markers

                ranking_table.append({  # Append compact leaderboard record
                    "strategy": name,
                    "total_return": tot_ret,
                    "cagr": cagr,
                    "sharpe": sharpe,
                    "max_drawdown": mdd,
                    "final_balance": final_bal,
                    "trades": trades,
                    "win_rate": m.get("Win Rate (%)", 0.0)
                })
            except Exception as e:
                print(f"Error running strategy '{name}': {e}")  # Isolate errors so 1 failing strategy doesn't break the other 4

        ranking_table.sort(key=lambda x: x["total_return"], reverse=True)  # Sort strategies highest-return-first
        for idx, row in enumerate(ranking_table, start=1):  # Assign 1-based rank (#1, #2, ..., #5)
            row["rank"] = idx

        currency = get_currency_symbol(ticker)  # Determine currency symbol for display

        return {  # Unified comparison response consumed by Shourya/comparison_view.py
            "ticker": ticker,
            "currency": currency,
            "initial_capital": float(initial_capital),
            "benchmark_result": bench_res,
            "strategy_results": strategy_results,
            "ranking": ranking_table,
            "df": df
        }
