# QuantSim v2.0 — Quantitative Stock Market Strategy Backtester

A full-stack desktop & web quantitative stock market strategy backtester built with **Python 3**, **FastAPI**, **NumPy**, **pandas**, **yfinance**, **PySide6**, **React + TypeScript**, **ShadCN UI**, and **TradingView Lightweight Charts v5**.

---

## 👥 Team Structure & Module Attribution

| Team Member | Folder | Assigned Responsibility | Documentation |
| :--- | :--- | :--- | :--- |
| **Shourya** | [`Shourya/`](./Shourya) | **ShadCN UI Workstation** (React + Tailwind + Radix primitives, `Ctrl+K` Command Palette, Theme Switcher, KPI Cards, Trade Log & Leaderboard) | [Shourya/README.md](./Shourya/README.md) |
| **Rounak** | [`Rounak/`](./Rounak) | **Code for the 5 Quantitative Trading Strategies** & `BaseStrategy` ABC | [Rounak/README.md](./Rounak/README.md) |
| **Prakshat** | [`Prakshat/`](./Prakshat) | **Finance API & Charts API Integration** (`yfinance`, Yahoo Search, CSV Cache, JSON Serializer & TradingView Lightweight Charts v5 React components) | [Prakshat/README.md](./Prakshat/README.md) |
| **Naman** | [`Naman/`](./Naman) | **Backend & Full App Bridge** (Metrics math, `BacktestEngine`, FastAPI REST server & PySide6 native desktop shell) | [Naman/README.md](./Naman/README.md) |

---

## 🚀 How to Run

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Launch the native desktop app (starts FastAPI locally + opens PySide6 window):
   ```bash
   python main.py
   ```
   Or open directly in your default web browser:
   ```bash
   python main.py --browser
   ```
3. *(Optional, only if editing `Shourya/src/` or `Prakshat/charts/`)* Rebuild the ShadCN frontend bundle:
   ```bash
   cd Shourya && npm install && npm run build
   ```
4. Run full automated verification (API endpoints, all 5 strategies, and desktop shell):
   ```bash
   python -m pytest -v
   ```
