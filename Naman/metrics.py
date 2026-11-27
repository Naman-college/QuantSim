"""
Naman/metrics.py - Quantitative Financial KPI & Drawdown Calculation Backend.
Member: Naman (Backend and Bridging Everyone's Work to Complete the Final App).

Academic Concepts Showcased:
- Vectorized NumPy array math (mean, std, sqrt, maximum.accumulate)
- Annualization across 252 market trading days and 365.25 calendar days
- Transparent, pure-math formulas without black-box finance libraries
"""

import numpy as np  # Vectorized numerical operations
import pandas as pd  # Time-series Series indexing and rolling/pct helpers
from typing import Dict, Any  # Return type hints


def calculate_metrics(equity_series: pd.Series, returns_series: pd.Series, initial_capital: float = 10000.0) -> Dict[str, Any]:
    """
    Computes standard portfolio performance KPIs from an equity curve and daily returns series.

    Parameters:
        equity_series (pd.Series): Daily portfolio value over time (in currency units)
        returns_series (pd.Series): Daily percentage returns (e.g. 0.015 for +1.5%)
        initial_capital (float): Starting cash balance on Day 0

    Returns:
        dict: Total Return (%), CAGR (%), Annualized Volatility (%), Sharpe Ratio,
              Max Drawdown (%), Win Rate (%), and Final Balance
    """
    if equity_series.empty or len(equity_series) < 2:  # Guard against degenerate < 2-day series
        return {  # Return safe zeroed defaults
            "Total Return (%)": 0.0,
            "CAGR (%)": 0.0,
            "Annualized Volatility (%)": 0.0,
            "Sharpe Ratio": 0.0,
            "Max Drawdown (%)": 0.0,
            "Win Rate (%)": 0.0,
            "Final Balance": initial_capital,
        }

    # 1. Total Return (%)
    final_balance = float(equity_series.iloc[-1])  # Portfolio balance on the final trading day
    total_return_pct = ((final_balance - initial_capital) / initial_capital) * 100.0 if initial_capital > 0 else 0.0  # Net percentage gain/loss

    # 2. Compound Annual Growth Rate (CAGR %)
    total_days = max((equity_series.index[-1] - equity_series.index[0]).days, 1)  # Calendar days between start & end (at least 1)
    years = total_days / 365.25  # Convert calendar days to fractional years (accounting for leap years)
    if years > 0 and final_balance > 0 and initial_capital > 0:  # Guard against non-positive values in fractional power
        cagr_pct = ((final_balance / initial_capital) ** (1.0 / years) - 1.0) * 100.0  # Annualized geometric growth rate
    else:
        cagr_pct = 0.0  # Fallback if equity hit <= 0

    # 3. Annualized Volatility (%)
    clean_returns = returns_series.dropna()  # Remove any NaN entries before statistical math
    daily_std = clean_returns.std()  # Sample standard deviation of daily returns
    annual_volatility_pct = (daily_std * np.sqrt(252)) * 100.0 if not np.isnan(daily_std) else 0.0  # Scale daily std by sqrt(252 trading days)

    # 4. Sharpe Ratio (risk-free rate assumed = 0 for educational clarity)
    daily_mean = clean_returns.mean()  # Average daily return
    if daily_std > 0 and not np.isnan(daily_std):  # Prevent division by zero when strategy never traded (std == 0)
        sharpe_ratio = (daily_mean / daily_std) * np.sqrt(252)  # Annualized risk-adjusted return
    else:
        sharpe_ratio = 0.0  # Zero Sharpe if return variance is zero

    # 5. Maximum Drawdown (MDD %)
    peak_equity = np.maximum.accumulate(equity_series.values)  # Running all-time peak equity up to each day
    peak_equity = np.where(peak_equity == 0, 1e-9, peak_equity)  # Replace 0 peaks with tiny epsilon to avoid division by zero
    drawdowns = (equity_series.values - peak_equity) / peak_equity  # Fractional decline from peak on every day (<= 0)
    max_drawdown_pct = min(0.0, float(np.min(drawdowns)) * 100.0)  # Worst peak-to-trough drop expressed as negative %

    # 6. Win Rate (% of active trading days that closed positive)
    active_days = clean_returns[clean_returns != 0]  # Filter out flat/cash days where return == 0
    if len(active_days) > 0:  # Only compute ratio if at least 1 active day occurred
        win_rate_pct = float((active_days > 0).mean()) * 100.0  # Fraction of positive active days * 100
    else:
        win_rate_pct = 0.0  # Zero win rate if no active trades took place

    return {  # Return rounded KPI dictionary consumed by UI cards, leaderboard, and tests
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
    Computes the daily underwater drawdown (%) series for plotting in ChartView.
    Formula: (Equity - Running_Peak) / Running_Peak * 100
    """
    peak = np.maximum.accumulate(equity_series.values)  # Running cumulative maximum equity
    peak = np.where(peak == 0, 1e-9, peak)  # Safe divisor guard
    drawdowns = (equity_series.values - peak) / peak * 100.0  # Percentage below prior peak on each day
    return pd.Series(drawdowns, index=equity_series.index)  # Wrap NumPy array back into date-indexed pandas Series
