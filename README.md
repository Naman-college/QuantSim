# Stock Market Strategy Backtester

A quantitative stock market strategy backtester built with **Python 3**, **NumPy**, and **pandas**, featuring a modern desktop interface inspired by the minimalist dark theme of [Linear.app](https://linear.app).

---

## 📌 Project Overview

This application allows students and investors to test 5 distinct investment and trading strategies across real-world historical data fetched dynamically from **Yahoo Finance (`yfinance`)** for both **US Markets** (S&P 500, Nasdaq, Megacap Tech) and **Indian Markets** (NSE Nifty 50, Sensex, Bluechips).

### The 5 Trading Strategies
1. **Lump Sum Investment**: 100% Day 1 allocation (Buy & Hold benchmark).
2. **Buying Dips**: Enters the market when price drops by a specified % (e.g. -2%) and holds for $N$ days.
3. **SIP (Systematic Investment Plan / DCA)**: Periodic fixed monthly/weekly cash additions accumulating shares over time.
4. **Target Gain & Stop Loss**: Buys the stock and automatically exits when reaching a target profit % or maximum allowed loss %.
5. **Moving Average Crossover**: Classic quantitative trend-following strategy using Fast and Slow Simple Moving Averages (Golden Cross & Death Cross).

---

## 📈 Professional Charting System (Google Finance & Screener Inspired)

The chart engine is powered by **TradingView Lightweight Charts** embedded inside PySide6 via `QWebEngineView`:
- **Google Finance Range Buttons**: One-click zooming for `1M`, `3M`, `6M`, `YTD`, `1Y`, and `ALL`.
- **Dynamic Auto-Scaling Y-Axis**: Smoothly adapts vertical scale to fit visible data while panning/zooming.
- **Interactive Crosshair HUD**: Live floating legend displaying Date, Strategy Equity, Benchmark Value, % Delta, and Trade Execution Badges.
- **Multi-View Switcher**: Instant switching between **Equity Curve ($)**, **Price / Candlesticks** (with SMA Fast/Slow overlays), and **Underwater Drawdown (%)**.
- **100% Offline-Capable**: Bundled locally with the standalone JS engine so it works without an internet connection.

---

## 👥 4-Person Team Distribution

| Team Member | Role | Files Owned | Concepts Explained in Viva |
| :--- | :--- | :--- | :--- |
| **Member 1** | **Data Ingestion** | `core/data_manager.py`<br>`config/presets.py` | `yfinance` download, pandas DatetimeIndex, `.ffill()`, `.dropna()`, local caching. |
| **Member 2** | **Quant Engine** | `core/engine.py`<br>`core/metrics.py` | Daily return calculations, `.shift(1)` to eliminate lookahead bias, `np.maximum.accumulate()` for drawdown, Sharpe ratio. |
| **Member 3** | **Strategy Developer** | `strategies/` (all 5 strategies) | Rolling windows (`.rolling().mean()`), conditional masks (`np.where()`), DCA mechanics. |
| **Member 4** | **UI/UX Developer** | `ui/` (`main_window.py`, `sidebar.py`, `chart_view.py`)<br>`config/theme.py` | PySide6 Qt layouts, Linear QSS styling (`#08090A` / `#5E6AD2`), interactive charts with PyQtGraph, Qt Signals & Slots. |

---

## 🚀 How to Run the App

1. Ensure dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```
2. Launch the desktop GUI:
   ```bash
   python main.py
   ```
3. Run automated verification tests:
   ```bash
   python tests/test_all_strategies.py
   ```

---

## 🧮 Simple Backend Calculations (Viva Reference)

```python
# 1. Market Return
df['Market_Return'] = df['Close'].pct_change()

# 2. Strategy Signal (Fast SMA > Slow SMA)
df['SMA_Fast'] = df['Close'].rolling(20).mean()
df['SMA_Slow'] = df['Close'].rolling(50).mean()
df['Signal'] = np.where(df['SMA_Fast'] > df['SMA_Slow'], 1, 0)

# 3. Strategy Return (shift(1) avoids lookahead bias)
df['Strategy_Return'] = df['Signal'].shift(1) * df['Market_Return']

# 4. Cumulative Equity
df['Equity'] = 10000 * (1 + df['Strategy_Return']).cumprod()

# 5. Maximum Drawdown
peak = np.maximum.accumulate(df['Equity'])
drawdown = (df['Equity'] - peak) / peak
max_drawdown = drawdown.min()
```
