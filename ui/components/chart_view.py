"""
chart_view.py - Professional TradingView Lightweight Charts embedded via QWebEngineView.
Maintained by Member 4 (UI/UX Developer).

Features:
- Google Finance / Screener style Range Buttons (1M, 3M, 6M, YTD, 1Y, ALL)
- Dynamic Auto-scaling Y-Axis on pan and zoom
- Interactive Crosshair with floating HUD Tooltip showing Date, Equity, Benchmark & % Delta
- Multi-view tabs: Strategy Equity ($), Candlesticks with SMA overlays, and Underwater Drawdown (%)
- 100% Offline-capable (bundled standalone lightweight-charts JS)
"""

import os
import json
import pandas as pd
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl
from config.theme import COLOR_SURFACE, COLOR_BORDER


class ChartView(QWidget):
    """
    Institutional-grade financial chart widget embedding TradingView Lightweight Charts.
    Communicates bidirectionally with the HTML/JS engine.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.web_view = QWebEngineView()
        self.web_view.setStyleSheet(f"background-color: {COLOR_SURFACE}; border: 1px solid {COLOR_BORDER}; border-radius: 8px;")
        layout.addWidget(self.web_view)

        self._is_loaded = False
        self._pending_payload = None

        # Resolve path to local chart.html template
        assets_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
        html_path = os.path.join(assets_dir, "chart.html")

        self.web_view.loadFinished.connect(self._on_page_loaded)
        self.web_view.load(QUrl.fromLocalFile(html_path))

    def _on_page_loaded(self, ok: bool):
        self._is_loaded = ok
        if ok and self._pending_payload:
            self._send_payload_to_js(self._pending_payload)
            self._pending_payload = None

    def plot_results(self, strat_df: pd.DataFrame, bench_df: pd.DataFrame, trade_events: list = None, currency: str = "$"):
        """Prepares JSON payload and passes it to TradingView Lightweight Charts."""
        if strat_df is None or strat_df.empty:
            return

        # 1. Equity Series Data
        equity_data = []
        for dt, row in strat_df.iterrows():
            date_str = str(dt)[:10]
            val = float(row['Equity']) if 'Equity' in row else 10000.0
            equity_data.append({"time": date_str, "value": round(val, 2)})

        # 2. Benchmark Series Data
        bench_data = []
        if bench_df is not None and not bench_df.empty:
            for dt, row in bench_df.iterrows():
                date_str = str(dt)[:10]
                val = float(row['Equity']) if 'Equity' in row else 10000.0
                bench_data.append({"time": date_str, "value": round(val, 2)})

        # 3. Candlestick Data (if OHLC available)
        candle_data = []
        for dt, row in strat_df.iterrows():
            date_str = str(dt)[:10]
            close_val = float(row['Close'])
            open_val = float(row['Open']) if 'Open' in row else close_val
            high_val = float(row['High']) if 'High' in row else max(open_val, close_val)
            low_val = float(row['Low']) if 'Low' in row else min(open_val, close_val)
            candle_data.append({
                "time": date_str,
                "open": round(open_val, 2),
                "high": round(high_val, 2),
                "low": round(low_val, 2),
                "close": round(close_val, 2),
            })

        # 4. Drawdown Data
        drawdown_data = []
        if 'Drawdown' in strat_df.columns:
            for dt, row in strat_df.iterrows():
                date_str = str(dt)[:10]
                drawdown_data.append({"time": date_str, "value": round(float(row['Drawdown']), 2)})

        # 5. Indicators (Fast & Slow MA if available)
        indicators = {}
        for f_key in ['MA_Fast', 'SMA_Fast']:
            if f_key in strat_df.columns:
                sma_fast = []
                for dt, row in strat_df.iterrows():
                    val = row[f_key]
                    if pd.notna(val):
                        sma_fast.append({"time": str(dt)[:10], "value": round(float(val), 2)})
                indicators["smaFast"] = sma_fast
                break

        for s_key in ['MA_Slow', 'SMA_Slow']:
            if s_key in strat_df.columns:
                sma_slow = []
                for dt, row in strat_df.iterrows():
                    val = row[s_key]
                    if pd.notna(val):
                        sma_slow.append({"time": str(dt)[:10], "value": round(float(val), 2)})
                indicators["smaSlow"] = sma_slow
                break

        # 6. Trade Markers
        markers = []
        if trade_events:
            for dt, price, action in trade_events:
                date_str = str(dt)[:10]
                markers.append({
                    "time": date_str,
                    "action": str(action)
                })

        payload = {
            "currency": currency,
            "equityData": equity_data,
            "benchmarkData": bench_data,
            "candleData": candle_data,
            "drawdownData": drawdown_data,
            "indicators": indicators,
            "markers": markers,
        }

        if self._is_loaded:
            self._send_payload_to_js(payload)
        else:
            self._pending_payload = payload

    def _send_payload_to_js(self, payload: dict):
        json_str = json.dumps(payload)
        self.web_view.page().runJavaScript(f"window.updateChartData({json_str});")
