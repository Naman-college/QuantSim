# Prakshat — Finance API & TradingView Charts API Integration

**Team Member:** Prakshat  
**Assigned Module:** Market Data Ingestion (`yfinance`, Yahoo Search REST API, CSV Cache), JSON Chart Serialization & TradingView Lightweight Charts v5 React Integration

---

## 📁 Folder Contents

| File | Purpose |
| :--- | :--- |
| `__init__.py` | Exposes `fetch_stock_data`, `search_stocks`, `PRESET_MARKETS`, and currency helpers. |
| `presets.py` | US & Indian market presets, `is_indian_ticker()`, and `get_currency_symbol()` (`$` / `₹`). |
| `data_manager.py` | Yahoo Finance (`yfinance`) OHLCV ingestion, DataFrame cleaning (`ffill`/`bfill`/`dropna`), timezone stripping, and CSV caching to `../data/`. |
| `stock_search.py` | Hybrid search combining a 100+ asset offline watchlist with live Yahoo Finance autocomplete (`query2.finance.yahoo.com`). |
| `preload_data.py` | Multi-threaded (`ThreadPoolExecutor`) CLI script to cache 100+ US & Indian assets in `../data/` for offline demos. |
| `chart_serializer.py` | Converts Rounak's pandas DataFrames (`Equity`, `OHLC`, `Drawdown`, `MA_Fast`, `MA_Slow`, `MA_Trend`, `trade_events`) into clean JSON for FastAPI. |
| `charts/chartTransformers.ts` | TypeScript interfaces, `en-IN` / `en-US` currency formatters, and TradingView v5 `BUY`/`SELL` marker converters. |
| `charts/SingleStrategyChart.tsx` | Interactive TradingView Lightweight Charts v5 component: Equity Area vs Buy & Hold dashed line, OHLC Candlesticks + SMA/EMA overlays, Underwater Drawdown %, `1M`–`ALL` zoom pills, and glassmorphic crosshair HUD. |
| `charts/ComparisonChart.tsx` | Multi-series TradingView Lightweight Charts v5 component overlaying all 5 strategy equity curves with a live crosshair floating legend. |

---

## 🔍 API & Charting Pipeline

1. **Finance Data Ingestion (`data_manager.py`, `stock_search.py`)**:
   - Checks `StockBackTest/data/<ticker>.csv` first; falls back to `yf.download(..., auto_adjust=True)` when needed and persists cleaned CSVs.
   - `search_stocks()` prioritizes instant local watchlist hits before querying Yahoo Finance's REST search endpoint (`timeout=3.5s`).
2. **Backend-to-Chart Serialization (`chart_serializer.py`)**:
   - Transforms pandas `DatetimeIndex` rows in a single pass into `{ time: "YYYY-MM-DD", value }` and `{ open, high, low, close }` arrays ready for JSON transport.
3. **TradingView Lightweight Charts v5 (`charts/SingleStrategyChart.tsx`, `charts/ComparisonChart.tsx`)**:
   - Uses `createChart()`, `AreaSeries`, `LineSeries`, `CandlestickSeries`, `createSeriesMarkers()`, `subscribeCrosshairMove()`, and a `ResizeObserver` so charts scale smoothly inside Shourya's responsive ShadCN grid and adapt automatically to Dark/Light theme switches.

---

## 🔗 Integration With Other Team Members
- **Consumed by Naman (Backend & API):** `Naman/engine.py` uses `fetch_stock_data()` & `get_currency_symbol()`, and `Naman/api.py` uses `search_stocks()`, `serialize_single_backtest()`, and `serialize_comparison_result()`.
- **Embedded by Shourya (UI):** `Shourya/src/App.tsx` and `ComparisonDashboard.tsx` import `SingleStrategyChart` and `ComparisonChart` via the `@prakshat/*` alias.

---

## 🎓 Teacher Viva / Oral Exam Prep (Likely Questions & Answers)

1. **Q: Why do you use `auto_adjust=True` in `yf.download()` and `tz_localize(None)` on the index?**  
   **A:** `auto_adjust=True` adjusts historical prices for stock splits and dividends so split dates don't look like crashes; `tz_localize(None)` removes exchange timezones so pandas date filtering never raises timezone mismatch errors.
2. **Q: How does `SingleStrategyChart.tsx` handle window resizing without clipping?**  
   **A:** It attaches a browser `ResizeObserver` to `containerRef`, calling `chart.applyOptions({ width, height })` whenever the ShadCN layout resizes.
3. **Q: How do Indian Rupee (`₹`) amounts get formatted differently from USD (`$`)?**  
   **A:** `formatCurrency()` in `chartTransformers.ts` selects `'en-IN'` locale grouping (lakhs/crores) when `currency === "₹"` and `'en-US'` otherwise.
4. **Q: Why separate `chart_serializer.py` from `BacktestEngine`?**  
   **A:** `BacktestEngine` works with pure pandas DataFrames (ideal for unit tests and quantitative analysis), while `chart_serializer.py` converts those DataFrames into JSON payloads formatted specifically for the TradingView Charts API.
