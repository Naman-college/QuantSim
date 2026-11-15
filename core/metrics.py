"""
metrics.py - Financial KPI calculations using NumPy and pandas.
Maintained by Member 2 (Quant Engine & Metrics).

Academic Concepts Showcased:
- NumPy vectorized calculations (mean, std, cumprod, maximum.accumulate)
- Time-series annualization using trading days (252 days)
- Pure math without external black-box libraries so students can explain each formula
"""

import numpy as np
import pandas as pd
from typing import Dict, Any


def calculate_metrics(equity_series: pd.Series, returns_series: pd.Series, initial_capital: float = 10000.0) -> Dict[str, Any]:
    """
    Computes standard financial performance metrics given an equity curve and daily returns.
    
    Parameters:
        equity_series (pd.Series): Daily portfolio value over time (in currency units)
        returns_series (pd.Series): Daily percentage returns of the strategy (e.g. 0.015 for +1.5%)
        initial_capital (float): Starting balance
        
    Returns:
        dict: Financial KPIs including Total Return, CAGR, Sharpe, Max Drawdown, and Win Rate
    """
    if equity_series.empty or len(equity_series) < 2:
        return {
            "Total Return (%)": 0.0,
            "CAGR (%)": 0.0,
            "Annualized Volatility (%)": 0.0,
            "Sharpe Ratio": 0.0,
            "Max Drawdown (%)": 0.0,
            "Win Rate (%)": 0.0,
            "Final Balance": initial_capital,
        }

    # 1. Total Return
    final_balance = float(equity_series.iloc[-1])
    total_return_pct = ((final_balance - initial_capital) / initial_capital) * 100.0 if initial_capital > 0 else 0.0

    # 2. CAGR (Compound Annual Growth Rate)
    # Formula: (End_Value / Start_Value) ** (1 / Years) - 1
    total_days = max((equity_series.index[-1] - equity_series.index[0]).days, 1)
    years = total_days / 365.25
    if years > 0 and final_balance > 0 and initial_capital > 0:
        cagr_pct = ((final_balance / initial_capital) ** (1.0 / years) - 1.0) * 100.0
    else:
        cagr_pct = 0.0

    # 3. Annualized Volatility
    # Std of daily returns * sqrt(252 trading days)
    clean_returns = returns_series.dropna()
    daily_std = clean_returns.std()
    annual_volatility_pct = (daily_std * np.sqrt(252)) * 100.0 if not np.isnan(daily_std) else 0.0

    # 4. Sharpe Ratio (assuming risk-free rate = 0 for simplicity)
    # Formula: (Mean Daily Return / Std Daily Return) * sqrt(252)
    daily_mean = clean_returns.mean()
    if daily_std > 0 and not np.isnan(daily_std):
        sharpe_ratio = (daily_mean / daily_std) * np.sqrt(252)
    else:
        sharpe_ratio = 0.0

    # 5. Maximum Drawdown (MDD)
    # peak = running maximum of equity
    # drawdown = (equity - peak) / peak
    peak_equity = np.maximum.accumulate(equity_series.values)
    # Avoid division by zero
    peak_equity = np.where(peak_equity == 0, 1e-9, peak_equity)
    drawdowns = (equity_series.values - peak_equity) / peak_equity
    max_drawdown_pct = min(0.0, float(np.min(drawdowns)) * 100.0)  # Most negative number, capped at 0

    # 6. Win Rate (%)
    # Percentage of active days where strategy made positive return
    active_days = clean_returns[clean_returns != 0]
    if len(active_days) > 0:
        win_rate_pct = float((active_days > 0).mean()) * 100.0
    else:
        win_rate_pct = 0.0


    return {
        "Total Return (%)": float(round(total_return_pct, 2)),
        "CAGR (%)": float(round(cagr_pct, 2)),
        "Annualized Volatility (%)": float(round(annual_volatility_pct, 2)),
        "Sharpe Ratio": float(round(sharpe_ratio, 2)),
        "Max Drawdown (%)": float(round(max_drawdown_pct, 2)),
        "Win Rate (%)": float(round(win_rate_pct, 2)),
        "Final Balance": float(round(final_balance, 2)),
    }


def calculate_drawdown_series(equity_series: pd.Series) -> pd.Series:
    """
    Computes underwater drawdown series as a percentage for plotting.
    
    Formula: (Equity - Running_Peak) / Running_Peak * 100
    """
    peak = np.maximum.accumulate(equity_series.values)
    drawdowns = (equity_series.values - peak) / peak * 100.0
    return pd.Series(drawdowns, index=equity_series.index)
