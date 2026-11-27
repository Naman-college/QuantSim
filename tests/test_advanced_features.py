"""
tests/test_advanced_features.py - Unit & integration tests for parameters, currencies, and Indian tickers.
"""

import sys  # Python path utilities
import os  # Filesystem path utilities
import pytest  # Pytest test runner

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Resolve project root directory
if ROOT_DIR not in sys.path:  # Ensure member folders are importable
    sys.path.insert(0, ROOT_DIR)  # Prepend project root

from Naman.engine import BacktestEngine  # Naman's backend orchestrator
from Prakshat.presets import get_currency_symbol  # Prakshat's currency helper
from Rounak.lump_sum import LumpSumStrategy  # Rounak's Strategy 1
from Rounak.buying_dips import BuyingDipsStrategy  # Rounak's Strategy 2
from Rounak.sip import SIPStrategy  # Rounak's Strategy 3
from Rounak.target_stop_loss import TargetStopLossStrategy  # Rounak's Strategy 4
from Rounak.moving_average import MovingAverageCrossoverStrategy  # Rounak's Strategy 5


def test_currency_symbols():
    """Verifies currency detection for US vs Indian tickers."""
    assert get_currency_symbol("SPY") == "$"  # US ETF uses USD
    assert get_currency_symbol("AAPL") == "$"  # US stock uses USD
    assert get_currency_symbol("RELIANCE.NS") == "₹"  # Pre-existing assertion from original suite
    assert get_currency_symbol("TCS.NS") == "₹"
    assert get_currency_symbol("^NSEI") == "₹"
    assert get_currency_symbol("^BSESN") == "₹"


def test_lump_sum_advanced_options():
    """Tests partial equity allocation with cash yield and transaction fee."""
    engine = BacktestEngine()
    res = engine.run_backtest(
        ticker="SPY",
        strategy_name="1. Lump Sum Investment",
        start_date="2023-01-01",
        initial_capital=50000.0,
        strategy_params={
            "allocation_pct": 70.0,
            "cash_interest_rate_pct": 4.5,
            "transaction_fee_pct": 0.1
        }
    )
    metrics = res["strategy_result"]["metrics"]
    assert "Final Balance" in metrics
    assert metrics["Final Balance"] > 0
    params = res["strategy_result"]["params"]
    assert "Equity Allocation" in params
    assert params["Equity Allocation"] == "70.0%"


def test_buying_dips_advanced_options():
    """Tests Buying Dips strategy parameter handling."""
    engine = BacktestEngine()
    res = engine.run_backtest(
        ticker="SPY",
        strategy_name="2. Buying Dips",
        start_date="2023-01-01",
        initial_capital=25000.0,
        strategy_params={
            "dip_pct": 1.5,
            "dip_window": 5,
            "hold_days": 15,
            "take_profit_pct": 4.0,
            "stop_loss_pct": 2.5,
            "transaction_fee_pct": 0.05
        }
    )
    metrics = res["strategy_result"]["metrics"]
    assert "Total Trades" in metrics
    params = res["strategy_result"]["params"]
    assert params["Lookback Window"] == "5 days"
    assert params["Take Profit"] == "+4.0%"
    assert params["Stop Loss"] == "-2.5%"


def test_sip_advanced_options():
    """Tests SIP strategy execution and metrics."""
    engine = BacktestEngine()
    res = engine.run_backtest(
        ticker="SPY",
        strategy_name="3. SIP (Systematic Investment Plan)",
        start_date="2023-01-01",
        initial_capital=5000.0,
        strategy_params={
            "monthly_installment": 1000.0,
            "frequency": "Bi-Weekly",
            "step_up_pct": 10.0,
            "dip_boost_pct": 20.0,
            "transaction_fee_pct": 0.05
        }
    )
    metrics = res["strategy_result"]["metrics"]
    assert metrics["Total Invested"] >= 5000.0
    assert metrics["Installments Count"] > 0
    assert "Net Profit" in metrics


def test_target_stop_loss_trailing():
    """Tests Target Gain & Stop Loss strategy with trailing stop enabled."""
    engine = BacktestEngine()
    res = engine.run_backtest(
        ticker="SPY",
        strategy_name="4. Target Gain & Stop Loss",
        start_date="2023-01-01",
        initial_capital=15000.0,
        strategy_params={
            "target_gain_pct": 6.0,
            "stop_loss_pct": 2.5,
            "trailing_stop": True,
            "trailing_stop_pct": 2.0,
            "max_hold_days": 20,
            "re_entry_wait_days": 2,
            "transaction_fee_pct": 0.1
        }
    )
    metrics = res["strategy_result"]["metrics"]
    assert "Take-Profit Exits" in metrics
    assert "Stop-Loss Exits" in metrics
    params = res["strategy_result"]["params"]
    assert params["Trailing Stop"] == "2.0%"


def test_moving_average_ema_and_trend_filter():
    """Tests Moving Average Crossover using EMA and 100-day SMA trend filter."""
    engine = BacktestEngine()
    res = engine.run_backtest(
        ticker="SPY",
        strategy_name="5. Moving Average Crossover",
        start_date="2023-01-01",
        initial_capital=20000.0,
        strategy_params={
            "fast_period": 10,
            "slow_period": 30,
            "ma_type": "EMA",
            "use_trend_filter": True,
            "trend_filter_period": 100,
            "stop_loss_pct": 4.0,
            "transaction_fee_pct": 0.1
        }
    )
    metrics = res["strategy_result"]["metrics"]
    assert "Total Trades" in metrics
    params = res["strategy_result"]["params"]
    assert "EMA" in params["MA Model"]
    assert params["Trend Filter"] == ">100 SMA"


def test_indian_ticker():
    """Tests running a backtest on an Indian NSE ticker (RELIANCE.NS)."""
    engine = BacktestEngine()
    res = engine.run_backtest(
        ticker="RELIANCE.NS",
        strategy_name="5. Moving Average Crossover",
        start_date="2023-01-01",
        initial_capital=100000.0
    )
    assert res["ticker"] == "RELIANCE.NS"
    metrics = res["strategy_result"]["metrics"]
    assert metrics["Final Balance"] > 0
