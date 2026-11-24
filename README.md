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
