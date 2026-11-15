"""
test_all_strategies.py - Automated test verifying all 5 strategies on real market data.
"""

import sys
import os
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from core.engine import BacktestEngine
from strategies import AVAILABLE_STRATEGIES


def test_strategies():
    engine = BacktestEngine()
    ticker = "SPY"
    start_date = "2023-01-01"

    print("=" * 60)
    print("RUNNING AUTOMATED VERIFICATION FOR ALL 5 STRATEGIES")
    print("=" * 60)

    for strat_name in AVAILABLE_STRATEGIES.keys():
        print(f"\nTesting: {strat_name} on {ticker}...")
        try:
            res = engine.run_backtest(
                ticker=ticker,
                strategy_name=strat_name,
                start_date=start_date,
                initial_capital=10000.0
            )
            strat_metrics = res["strategy_result"]["metrics"]
            bench_metrics = res["benchmark_result"]["metrics"]
            trades = len(res["strategy_result"]["trade_events"])
            
            print(f"  [PASS] {strat_name}")
            print(f"         Total Return: {strat_metrics.get('Total Return (%)')}%")
            print(f"         CAGR: {strat_metrics.get('CAGR (%)')}%")
            print(f"         Max Drawdown: {strat_metrics.get('Max Drawdown (%)')}%")
            print(f"         Trades Generated: {trades}")
        except Exception as e:
            print(f"  [FAIL] {strat_name}: {e}")
            raise e

    print("\n" + "=" * 60)
    print("ALL 5 STRATEGIES PASSED VERIFICATION!")
    print("=" * 60)


if __name__ == "__main__":
    test_strategies()
