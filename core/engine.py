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
