"""
comparison_view.py - Combined Multi-Strategy Comparison & Ranking Dashboard.
Maintained by Member 4 (UI/UX Developer) & Member 2 (Quant Engine).
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView, QFrame, QSplitter
)
from PySide6.QtCore import Qt
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl
import os
import json
from config.theme import (
    COLOR_SURFACE, COLOR_SURFACE_ELEVATED, COLOR_BORDER,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_SUCCESS,
    COLOR_DANGER, COLOR_ACCENT
)

STRATEGY_COLORS = {
    "1. Lump Sum Investment": "#8A8F98",            # Muted Slate Baseline
    "2. Buying Dips": "#10B981",                    # Emerald Green (Accent 2)
    "3. SIP (Systematic Investment Plan)": "#818CF8", # Soft Indigo (Accent 1 tint)
    "4. Target Gain & Stop Loss": "#34D399",        # Mint Green (Accent 2 tint)
    "5. Moving Average Crossover": "#5E6AD2",       # Electric Indigo (Accent 1)
}


from ui.components.kpi_card import KPICard


class ComparisonView(QWidget):
    """
    Unified comparison tab displaying:
    1. 4 Top Comparative KPI Cards (Best Return, Lowest Drawdown, Best Sharpe, Scope)
    2. Horizontal Resizable Splitter:
       - Left/Center: Multi-line overlay chart of all 5 strategies
       - Right Panel: Comprehensive performance ranking leaderboard & insight takeaway
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # ----------------------------------------------------
        # 1. Top Section: 4 Comparative Summary Cards
        # ----------------------------------------------------
        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(10)

        self.kpi_top_return = KPICard("Top Strategy Return")
        self.kpi_lowest_mdd = KPICard("Lowest Drawdown")
        self.kpi_best_sharpe = KPICard("Best Sharpe Ratio")
        self.kpi_scope = KPICard("Strategies Evaluated")

        kpi_layout.addWidget(self.kpi_top_return)
        kpi_layout.addWidget(self.kpi_lowest_mdd)
        kpi_layout.addWidget(self.kpi_best_sharpe)
        kpi_layout.addWidget(self.kpi_scope)
        layout.addLayout(kpi_layout)

        # ----------------------------------------------------
        # 2. Main Area: Horizontal Resizable Splitter
        # ----------------------------------------------------
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background-color: {COLOR_BORDER};
                width: 4px;
            }}
            QSplitter::handle:hover {{
                background-color: {COLOR_ACCENT};
            }}
        """)

        # Left/Center: Embedded Multi-Line Chart
        self.web_view = QWebEngineView()
        self.web_view.setStyleSheet(f"background-color: {COLOR_SURFACE}; border: 1px solid {COLOR_BORDER}; border-radius: 8px;")
        
        assets_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
        html_path = os.path.join(assets_dir, "comparison_chart.html")
        self._is_loaded = False
        self._pending_payload = None

        self.web_view.loadFinished.connect(self._on_chart_loaded)
        self.web_view.load(QUrl.fromLocalFile(html_path))
        self.splitter.addWidget(self.web_view)

        # Right: Ranking Leaderboard Panel
        right_panel = QFrame()
        right_panel.setObjectName("cardPanel")
        right_panel.setMinimumWidth(320)
        right_panel.setStyleSheet(f"""
            QFrame#cardPanel {{
                background-color: {COLOR_SURFACE};
                border: 1px solid {COLOR_BORDER};
                border-radius: 8px;
            }}
        """)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(12, 14, 12, 12)
        right_layout.setSpacing(8)

        # Leaderboard Header
        header_row = QHBoxLayout()
        lbl_title = QLabel("STRATEGY LEADERBOARD")
        lbl_title.setObjectName("sectionHeader")
        header_row.addWidget(lbl_title)

        self.lbl_summary = QLabel("All 5 Strategies")
        self.lbl_summary.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 11px;")
        header_row.addStretch()
        header_row.addWidget(self.lbl_summary)
        right_layout.addLayout(header_row)

        # Leaderboard Table
        self.rank_table = QTableWidget()
        self.rank_table.setColumnCount(6)
        self.rank_table.setHorizontalHeaderLabels([
            "#", "STRATEGY", "RETURN", "CAGR", "SHARPE", "MAX DD"
        ])
        self.rank_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.rank_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.rank_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.rank_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.rank_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.rank_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.rank_table.verticalHeader().setVisible(False)
        self.rank_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.rank_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.rank_table.setAlternatingRowColors(True)
        self.rank_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {COLOR_SURFACE};
                alternate-background-color: #121318;
                border: 1px solid {COLOR_BORDER};
                border-radius: 6px;
                gridline-color: transparent;
                color: {COLOR_TEXT_PRIMARY};
            }}
            QTableWidget::item {{
                padding: 6px 8px;
                border-bottom: 1px solid {COLOR_BORDER};
            }}
        """)
        right_layout.addWidget(self.rank_table, stretch=1)

        # Bottom Insight Box
        self.insight_box = QFrame()
        self.insight_box.setStyleSheet(f"""
            QFrame {{
                background-color: #14161E;
                border: 1px solid {COLOR_BORDER};
                border-left: 3px solid {COLOR_ACCENT};
                border-radius: 6px;
                padding: 8px 10px;
            }}
        """)
        insight_layout = QVBoxLayout(self.insight_box)
        insight_layout.setContentsMargins(6, 6, 6, 6)
        insight_layout.setSpacing(3)

        lbl_insight_title = QLabel("KEY QUANT TAKEAWAY")
        lbl_insight_title.setStyleSheet(f"color: {COLOR_ACCENT}; font-size: 10px; font-weight: 700; letter-spacing: 0.5px;")
        insight_layout.addWidget(lbl_insight_title)

        self.lbl_insight_body = QLabel("Switch to this tab to compare all 5 strategies on the selected asset.")
        self.lbl_insight_body.setWordWrap(True)
        self.lbl_insight_body.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 11px; line-height: 1.3;")
        insight_layout.addWidget(self.lbl_insight_body)

        right_layout.addWidget(self.insight_box)

        self.splitter.addWidget(right_panel)
        self.splitter.setStretchFactor(0, 3)  # Chart takes ~62%
        self.splitter.setStretchFactor(1, 2)  # Leaderboard takes ~38%
        self.splitter.setSizes([750, 420])

        layout.addWidget(self.splitter, stretch=1)

    def _on_chart_loaded(self, ok: bool):
        self._is_loaded = ok
        if ok and self._pending_payload:
            self._send_payload_to_js(self._pending_payload)
            self._pending_payload = None

    def show_loading(self, msg: str = "Simulating all 5 strategies..."):
        if self._is_loaded:
            self.web_view.page().runJavaScript(f"window.showLoading('{msg}');")

    def hide_loading(self):
        if self._is_loaded:
            self.web_view.page().runJavaScript("window.hideLoading();")

    def update_comparison_data(self, comparison_result: dict):
        """Populates multi-line chart, summary KPI cards, and leaderboard with backtest results."""
        if not comparison_result:
            return

        ticker = comparison_result.get("ticker", "")
        currency = comparison_result.get("currency", "$")
        initial_cap = comparison_result.get("initial_capital", 10000.0)
        rankings = comparison_result.get("ranking", [])
        strat_results = comparison_result.get("strategy_results", {})

        if not rankings:
            return

        # ----------------------------------------------------
        # 1. Update 4 Top Summary KPI Cards
        # ----------------------------------------------------
        winner = rankings[0]
        self.kpi_top_return.set_value(
            value=f"{winner['total_return']:+.2f}%",
            sub_text=f"Winner: {winner['strategy']}",
            is_positive=(winner['total_return'] >= 0)
        )

        # Lowest Drawdown (closest to 0%)
        safest = min(rankings, key=lambda r: abs(r['max_drawdown']))
        self.kpi_lowest_mdd.set_value(
            value=f"{safest['max_drawdown']:.2f}%",
            sub_text=f"Safest: {safest['strategy']}",
            is_positive=(safest['max_drawdown'] > -15.0)
        )

        # Best Sharpe
        best_sharpe = max(rankings, key=lambda r: r['sharpe'])
        self.kpi_best_sharpe.set_value(
            value=f"{best_sharpe['sharpe']:.2f}",
            sub_text=f"Best Risk-Adj: {best_sharpe['strategy']}",
            is_positive=(best_sharpe['sharpe'] > 0.8)
        )

        self.kpi_scope.set_value(
            value=f"{len(rankings)} of 5 Done",
            sub_text=f"Asset: {ticker} (Full Range)",
            is_positive=True
        )

        # Update Key Takeaway Note
        self.lbl_insight_body.setText(
            f"Top performer for {ticker} is {winner['strategy']} ({winner['total_return']:+.1f}%). "
            f"Safest profile is {safest['strategy']} with minimal drawdown of {safest['max_drawdown']:.1f}%."
        )

        # ----------------------------------------------------
        # 2. Update Leaderboard Table
        # ----------------------------------------------------
        self.rank_table.setRowCount(0)
        self.rank_table.setRowCount(len(rankings))

        for row, r in enumerate(rankings):
            rank = r["rank"]
            strat_name = r["strategy"]
            tot_ret = r["total_return"]
            cagr = r["cagr"]
            sharpe = r["sharpe"]
            mdd = r["max_drawdown"]
            bal = r["final_balance"]
            trades = r["trades"]

            # Rank Badge (#1 Emerald Green, others subtle Linear border)
            badge_text = f" #{rank} "
            if rank == 1:
                badge_style = f"color: {COLOR_SUCCESS}; background-color: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.4);"
            else:
                badge_style = f"color: {COLOR_TEXT_SECONDARY}; background-color: #16181D; border: 1px solid {COLOR_BORDER};"

            rank_badge = QLabel(badge_text)
            rank_badge.setStyleSheet(f"{badge_style} border-radius: 4px; font-weight: 700; font-size: 11px; padding: 2px 6px;")
            container_w = QWidget()
            cw_layout = QHBoxLayout(container_w)
            cw_layout.setContentsMargins(4, 2, 4, 2)
            cw_layout.addWidget(rank_badge)
            cw_layout.addStretch()
            self.rank_table.setCellWidget(row, 0, container_w)

            # Strategy Name with color dot
            color_dot = STRATEGY_COLORS.get(strat_name, COLOR_ACCENT)
            item_strat = QTableWidgetItem(f"●  {strat_name}")
            item_strat.setToolTip(f"Final Balance: {currency}{bal:,.2f} | Trades: {trades}")
            self.rank_table.setItem(row, 1, item_strat)

            # Total Return
            ret_item = QTableWidgetItem(f"{tot_ret:+.2f}%")
            ret_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            ret_item.setForeground(Qt.GlobalColor.green if tot_ret >= 0 else Qt.GlobalColor.red)
            ret_item.setToolTip(f"Final Balance: {currency}{bal:,.2f}")
            self.rank_table.setItem(row, 2, ret_item)

            # CAGR
            cagr_item = QTableWidgetItem(f"{cagr:+.1f}%")
            cagr_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.rank_table.setItem(row, 3, cagr_item)

            # Sharpe
            sharpe_item = QTableWidgetItem(f"{sharpe:.2f}")
            sharpe_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.rank_table.setItem(row, 4, sharpe_item)

            # Max Drawdown
            mdd_item = QTableWidgetItem(f"{mdd:.1f}%")
            mdd_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            mdd_item.setForeground(Qt.GlobalColor.red)
            self.rank_table.setItem(row, 5, mdd_item)

        self.lbl_summary.setText(f"Top: {winner['strategy']}")

        # ----------------------------------------------------
        # 3. Build multi-series JSON payload for the comparison chart
        # ----------------------------------------------------
        lines = []
        for name, res in strat_results.items():
            df = res.get("df")
            if df is None or df.empty or 'Equity' not in df.columns:
                continue
            
            series_data = []
            for dt, row in df.iterrows():
                series_data.append({
                    "time": str(dt)[:10],
                    "value": round(float(row['Equity']), 2)
                })

            lines.append({
                "name": name,
                "color": STRATEGY_COLORS.get(name, COLOR_ACCENT),
                "data": series_data
            })

        payload = {
            "currency": currency,
            "ticker": ticker,
            "lines": lines
        }

        if self._is_loaded:
            self._send_payload_to_js(payload)
        else:
            self._pending_payload = payload

    def _send_payload_to_js(self, payload: dict):
        json_str = json.dumps(payload)
        self.web_view.page().runJavaScript(f"window.updateComparisonChart({json_str});")
