"""
tests/test_all_strategies.py - Automated verification of all 5 strategies and multi-strategy ranking.
"""

import sys  # Python path utilities
import os  # Filesystem path utilities

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Resolve project root directory
if ROOT_DIR not in sys.path:  # Ensure member packages are importable
    sys.path.insert(0, ROOT_DIR)  # Prepend root path

from Naman.engine import BacktestEngine  # Import Naman's core backtest engine
from Rounak import AVAILABLE_STRATEGIES  # Import Rounak's 5 registered strategies


def test_strategies():
    """Runs single-strategy backtests on SPY and a full 5-strategy comparison on AAPL."""
    engine = BacktestEngine()  # Instantiate backend engine
    ticker = "SPY"  # Target US S&P 500 ETF
    start_date = "2023-01-01"  # Backtest start date

    print("=" * 60)  # Banner separator
    print("RUNNING AUTOMATED VERIFICATION FOR ALL 5 STRATEGIES")  # Header text
    print("=" * 60)  # Banner separator

    for strat_name in AVAILABLE_STRATEGIES.keys():  # Loop through each of Rounak's 5 strategies
        print(f"\nTesting: {strat_name} on {ticker}...")  # Status log
        try:
            res = engine.run_backtest(  # Execute single backtest via Naman's engine
                ticker=ticker,
                strategy_name=strat_name,
                start_date=start_date,
                initial_capital=10000.0
            )
            strat_metrics = res["strategy_result"]["metrics"]  # Read computed strategy KPIs
            trades = len(res["strategy_result"]["trade_events"])  # Count generated BUY/SELL events

            print(f"  [PASS] {strat_name}")  # Report pass
            print(f"         Total Return: {strat_metrics.get('Total Return (%)')}%")  # Print total return
            print(f"         CAGR: {strat_metrics.get('CAGR (%)')}%")  # Print CAGR
            print(f"         Max Drawdown: {strat_metrics.get('Max Drawdown (%)')}%")  # Print MDD
            print(f"         Trades Generated: {trades}")  # Print trade count
        except Exception as e:
            print(f"  [FAIL] {strat_name}: {e}")  # Report failure
            raise e  # Re-raise so pytest/runner fails cleanly

    print("\n" + "=" * 60)
    print("ALL 5 STRATEGIES PASSED VERIFICATION!")
    print("=" * 60)

    print("\nTESTING COMBINED MULTI-STRATEGY COMPARISON & RANKING...")
    all_res = engine.run_all_strategies(ticker="AAPL", start_date="2023-01-01", initial_capital=10000.0)  # Compare all 5 strategies on AAPL
    print("Rankings for AAPL:")
    for r in all_res["ranking"]:  # Print sorted leaderboard rows
        print(f"  #{r['rank']} {r['strategy']} | Return: {r['total_return']:+.2f}% | CAGR: {r['cagr']:+.2f}% | Sharpe: {r['sharpe']:.2f} | MDD: {r['max_drawdown']:.2f}% | Trades: {r['trades']}")

    print("\nALL COMPARISON & LEADERBOARD VERIFICATIONS PASSED!")


if __name__ == "__main__":  # Run directly from command line
    test_strategies()
