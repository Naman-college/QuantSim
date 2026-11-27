# Naman — Backend Engine, FastAPI Server & Full App Bridge

**Team Member:** Naman  
**Assigned Module:** Quantitative Metrics Backend, `BacktestEngine`, FastAPI REST API (`api.py`), and Native PySide6 + Uvicorn Application Shell (`app.py`)

---

## 📁 Folder Contents

| File | Purpose |
| :--- | :--- |
| `__init__.py` | Package declaration exposing `metrics`, `engine`, `api`, and `app`. |
| `metrics.py` | Pure NumPy/pandas financial KPI formulas: Total Return, CAGR, Annualized Volatility, Sharpe Ratio, Max Drawdown, Win Rate, and Underwater Drawdown series. |
| `engine.py` | `BacktestEngine` orchestrating Prakshat's `fetch_stock_data()` + Rounak's 5 strategies + Naman's `metrics.py`. |
| `api.py` | FastAPI application exposing `/api/health`, `/api/strategies`, `/api/presets`, `/api/search`, `/api/backtest`, `/api/compare`, and serving Shourya's compiled ShadCN UI (`Shourya/dist/`). |
| `app.py` | Starts Uvicorn on a free localhost port in a background daemon thread and opens a native **PySide6 `QMainWindow` + `QWebEngineView`** desktop window (or opens in default browser with `--browser`). |

---

## ⚙️ Full-Stack Bridge Architecture

```
  Shourya (ShadCN UI in QWebEngineView / Browser)
        │   GET  /api/search?q=...
        │   POST /api/backtest
        │   POST /api/compare
        ▼
  Naman/api.py (FastAPI + Pydantic validation)
        │
        ├──▶ Prakshat/stock_search.py        (Hybrid local + Yahoo Finance search)
        ├──▶ Naman/engine.py (BacktestEngine)
        │       ├──▶ Prakshat/data_manager.py (yfinance + CSV cache)
        │       ├──▶ Rounak/*.py              (5 Strategies + BaseStrategy)
        │       └──▶ Naman/metrics.py         (NumPy/pandas KPI math)
        └──▶ Prakshat/chart_serializer.py    (JSON response for TradingView Charts)
```

---

## 🎓 Teacher Viva / Oral Exam Prep (Likely Questions & Answers)

1. **Q: Why do you use `np.sqrt(252)` for Volatility and Sharpe Ratio, but `365.25` for CAGR?**  
   **A:** Volatility and Sharpe Ratio annualize **daily trading returns** (~252 market trading days/year), whereas CAGR measures compound growth between **calendar dates** (~365.25 days/year).
2. **Q: How does `python main.py` launch a web-tech ShadCN UI as a native desktop app without requiring a manual server startup?**  
   **A:** `Naman/app.py` finds an available port on `127.0.0.1`, launches FastAPI/Uvicorn inside a background `daemon=True` thread, polls `/api/health` until ready, and loads `http://127.0.0.1:<port>/` inside PySide6's embedded Chromium `QWebEngineView`.
3. **Q: Why use Pydantic `BaseModel` schemas (`BacktestRequest`, `CompareRequest`) in `Naman/api.py`?**  
   **A:** Pydantic automatically validates types, non-empty ticker strings, and positive `initial_capital > 0`, returning clean HTTP `422` validation errors before invalid inputs reach `BacktestEngine`.
4. **Q: How does `np.maximum.accumulate()` compute Maximum Drawdown?**  
   **A:** It computes the running peak equity at every bar in vectorized C speed; `(equity - peak) / peak` gives every day's underwater decline, and `np.min()` finds the worst drop.
