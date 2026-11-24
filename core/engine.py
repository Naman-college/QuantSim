"""
engine.py - Core backtesting coordinator.
Maintained by Member 2 (Quant Engine & Metrics).

Coordinates data fetching, strategy execution, and benchmark comparison.
"""

from typing import Dict, Any
import pandas as pd
from core.data_manager import fetch_stock_data
from strategies import AVAILABLE_STRATEGIES
from strategies.lump_sum import LumpSumStrategy


class BacktestEngine:
    """
    Central engine orchestrating the backtest workflow:
    1. Fetch and clean price history from yfinance
    2. Run selected strategy
    3. Run benchmark (Lump Sum / Buy & Hold) for direct comparison
    """

    def __init__(self):
        self.strategies = AVAILABLE_STRATEGIES
        self.benchmark_strategy = LumpSumStrategy()

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
        Executes a backtest for the specified ticker and strategy.
        
        Returns:
            dict containing:
                - 'ticker': ticker symbol
                - 'strategy_name': selected strategy name
                - 'strategy_result': DataFrame and metrics of strategy
                - 'benchmark_result': DataFrame and metrics of Buy & Hold benchmark
        """
        if strategy_name not in self.strategies:
            raise ValueError(f"Unknown strategy '{strategy_name}'. Available: {list(self.strategies.keys())}")

        strategy_params = strategy_params or {}

        # 1. Download / Load cached price data
        df = fetch_stock_data(ticker=ticker, start_date=start_date, end_date=end_date)
        if df.empty or len(df) < 5:
            raise ValueError(f"Insufficient historical data points for ticker '{ticker}'.")

        # 2. Run the chosen strategy
        strategy = self.strategies[strategy_name]
        strat_res = strategy.run(df=df, initial_capital=initial_capital, **strategy_params)

        # 3. Run Benchmark (Lump Sum / Buy & Hold) for side-by-side comparison
        bench_res = self.benchmark_strategy.run(df=df, initial_capital=initial_capital)

        from config.presets import get_currency_symbol
        currency = get_currency_symbol(ticker)

        return {
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
        Executes ALL available strategies on the given stock data using the same cached
        price history, ranks them by Total Return and Sharpe ratio, and computes comparative curves.
        """
        strategy_params_dict = strategy_params_dict or {}

        # 1. Fetch data once
        df = fetch_stock_data(ticker=ticker, start_date=start_date, end_date=end_date)
        if df.empty or len(df) < 5:
            raise ValueError(f"Insufficient historical data points for ticker '{ticker}'.")

        # 2. Benchmark (Lump Sum)
        bench_res = self.benchmark_strategy.run(df=df, initial_capital=initial_capital)

        # 3. Execute each strategy
        strategy_results = {}
        ranking_table = []

        for name, strategy in self.strategies.items():
            params = strategy_params_dict.get(name, {})
            try:
                res = strategy.run(df=df, initial_capital=initial_capital, **params)
                strategy_results[name] = res
                m = res["metrics"]
                tot_ret = m.get("Total Return (%)", 0.0)
                sharpe = m.get("Sharpe Ratio", 0.0)
                mdd = m.get("Max Drawdown (%)", 0.0)
                cagr = m.get("CAGR (%)", 0.0)
                final_bal = m.get("Final Balance", initial_capital)
                trades = len(res.get("trade_events", []))

                ranking_table.append({
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
                print(f"Error running strategy '{name}': {e}")

        # Rank by Total Return descending
        ranking_table.sort(key=lambda x: x["total_return"], reverse=True)
        for idx, row in enumerate(ranking_table, start=1):
            row["rank"] = idx

        from config.presets import get_currency_symbol
        currency = get_currency_symbol(ticker)

        return {
            "ticker": ticker,
            "currency": currency,
            "initial_capital": float(initial_capital),
            "benchmark_result": bench_res,
            "strategy_results": strategy_results,
            "ranking": ranking_table,
            "df": df
        }
