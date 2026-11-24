"""
main_window.py - Main Window with 3-column layout & Multi-Strategy Comparison Tab.
Maintained by Member 4 (UI/UX Developer) & Member 1 (Project Lead).
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QMessageBox, QLabel, QStatusBar, QFrame, QTabWidget,
    QSplitter
)
from PySide6.QtCore import Qt, QThread, Signal
from ui.components.sidebar import Sidebar
from ui.components.kpi_card import KPICard
from ui.components.chart_view import ChartView
from ui.components.trade_table import TradeTable
from ui.components.comparison_view import ComparisonView
from core.engine import BacktestEngine
from config.theme import (
    COLOR_CANVAS, COLOR_SURFACE, COLOR_BORDER,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_ACCENT
)


class BacktestWorker(QThread):
    """Background worker thread so heavy data downloads and calculations don't freeze the GUI."""
    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, engine: BacktestEngine, payload: dict):
        super().__init__()
        self.engine = engine
        self.payload = payload

    def run(self):
        try:
            result = self.engine.run_backtest(
                ticker=self.payload["ticker"],
                strategy_name=self.payload["strategy_name"],
                start_date=self.payload["start_date"],
                initial_capital=self.payload["capital"],
                strategy_params=self.payload["params"]
            )
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class ComparisonWorker(QThread):
    """Worker thread to run all 5 strategies simultaneously and rank performance."""
    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, engine: BacktestEngine, payload: dict):
        super().__init__()
        self.engine = engine
        self.payload = payload

    def run(self):
        try:
            result = self.engine.run_all_strategies(
                ticker=self.payload["ticker"],
                start_date=self.payload["start_date"],
                initial_capital=self.payload["capital"],
                strategy_params_dict=self.payload.get("all_params", {})
            )
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    """
    QuantSim Main Application Window featuring:
    - Left Column: Resizable Search & Settings Sidebar (~280-320px)
    - Tab 1: Single Strategy Deep-Dive (KPIs, TradingView Chart, Resizable Trade Activity Log)
    - Tab 2: Strategy Comparison & Leaderboard (Summary KPIs, 5-Curve Overlay Chart, Resizable Leaderboard)
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QuantSim — Quantitative Strategy Backtester")
        self.resize(1380, 860)
        self.engine = BacktestEngine()
        self.worker = None
        self.comp_worker = None
        self.is_comparing = False
        self.last_compared_key = None

        self._setup_ui()

        # Initial backtest on startup
        self.sidebar._emit_run()

    def _setup_ui(self):
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(0)

        # ----------------------------------------------------
        # Outer Horizontal Splitter (Sidebar | Main Content)
        # ----------------------------------------------------
        self.outer_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.outer_splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background-color: {COLOR_BORDER};
                width: 4px;
            }}
            QSplitter::handle:hover {{
                background-color: {COLOR_ACCENT};
            }}
        """)

        # 1. Left Column: Control Sidebar
        self.sidebar = Sidebar()
        self.sidebar.run_backtest_signal.connect(self._start_backtest)
        self.sidebar.stock_changed.connect(self._on_stock_changed)
        self.outer_splitter.addWidget(self.sidebar)

        # 2. Main Content Area: Styled QTabWidget
        self.tabs = QTabWidget()
        self.tabs.setObjectName("mainTabs")
        self.tabs.setDocumentMode(True)

        # --- TAB 1: Single Strategy Analysis ---
        single_tab_widget = QWidget()
        single_tab_layout = QHBoxLayout(single_tab_widget)
        single_tab_layout.setContentsMargins(4, 6, 0, 0)
        single_tab_layout.setSpacing(0)

        # Single Strategy Splitter (Center Chart | Right Trade Log)
        self.single_tab_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.single_tab_splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background-color: {COLOR_BORDER};
                width: 4px;
            }}
            QSplitter::handle:hover {{
                background-color: {COLOR_ACCENT};
            }}
        """)

        # Center Column: KPI Cards & TradingView Chart
        center_container = QWidget()
        center_layout = QVBoxLayout(center_container)
        center_layout.setContentsMargins(0, 0, 6, 0)
        center_layout.setSpacing(10)

        # KPI Metric Cards
        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(10)

        self.kpi_return = KPICard("Total Return")
        self.kpi_cagr = KPICard("CAGR")
        self.kpi_mdd = KPICard("Max Drawdown")
        self.kpi_balance = KPICard("Final Balance")

        kpi_layout.addWidget(self.kpi_return)
        kpi_layout.addWidget(self.kpi_cagr)
        kpi_layout.addWidget(self.kpi_mdd)
        kpi_layout.addWidget(self.kpi_balance)
        center_layout.addLayout(kpi_layout)

        # TradingView Interactive Chart
        self.chart_view = ChartView()
        center_layout.addWidget(self.chart_view, stretch=1)
        self.single_tab_splitter.addWidget(center_container)

        # Right Column: Trade Activity Log (~320px resizable)
        right_panel = QFrame()
        right_panel.setObjectName("cardPanel")
        right_panel.setMinimumWidth(280)
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

        trade_header_layout = QHBoxLayout()
        trade_title = QLabel("TRADE ACTIVITY LOG")
        trade_title.setObjectName("sectionHeader")
        trade_header_layout.addWidget(trade_title)

        self.lbl_trade_count = QLabel("0 trades")
        self.lbl_trade_count.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 11px;")
        trade_header_layout.addStretch()
        trade_header_layout.addWidget(self.lbl_trade_count)
        right_layout.addLayout(trade_header_layout)

        self.trade_table = TradeTable()
        right_layout.addWidget(self.trade_table, stretch=1)
        self.single_tab_splitter.addWidget(right_panel)

        self.single_tab_splitter.setStretchFactor(0, 3)
        self.single_tab_splitter.setStretchFactor(1, 1)
        self.single_tab_splitter.setSizes([780, 320])

        single_tab_layout.addWidget(self.single_tab_splitter)
        self.tabs.addTab(single_tab_widget, "  Single Strategy Backtest  ")

        # --- TAB 2: Multi-Strategy Comparison & Leaderboard ---
        comparison_tab_widget = QWidget()
        comp_layout = QVBoxLayout(comparison_tab_widget)
        comp_layout.setContentsMargins(4, 6, 0, 0)
        comp_layout.setSpacing(0)

        self.comparison_view = ComparisonView()
        comp_layout.addWidget(self.comparison_view)

        self.tabs.addTab(comparison_tab_widget, "  All Strategies Comparison  ")
        self.tabs.currentChanged.connect(self._on_tab_changed)

        self.outer_splitter.addWidget(self.tabs)
        self.outer_splitter.setStretchFactor(0, 0)
        self.outer_splitter.setStretchFactor(1, 1)
        self.outer_splitter.setSizes([290, 1090])

        main_layout.addWidget(self.outer_splitter)

        self.setCentralWidget(central_widget)

        # Minimalist Status Bar
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet(f"background-color: {COLOR_SURFACE}; color: {COLOR_TEXT_SECONDARY}; border-top: 1px solid {COLOR_BORDER};")
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready. Search an asset or choose parameters to backtest.")

    def _on_tab_changed(self, index: int):
        if index == 1:
            payload = self.sidebar.get_current_payload()
            key = (payload["ticker"], payload["start_date"], payload["capital"])
            if self.last_compared_key != key and not self.is_comparing:
                self._start_comparison(payload)

    def _on_stock_changed(self, symbol: str):
        payload = self.sidebar.get_current_payload()
        if self.tabs.currentIndex() == 1:
            self._start_comparison(payload)
        else:
            self._start_backtest(payload)

    def _start_backtest(self, payload: dict):
        if self.worker and self.worker.isRunning():
            return

        ticker = payload["ticker"]
        strat = payload["strategy_name"]
        self.status_bar.showMessage(f"Fetching data and calculating backtest for {ticker} ({strat})...")
        self.sidebar.btn_run.setEnabled(False)
        self.sidebar.btn_run.setText("Calculating...")

        if self.tabs.currentIndex() != 0:
            self.tabs.setCurrentIndex(0)

        self.chart_view.show_loading(f"Simulating {strat} on {ticker}...")

        self.worker = BacktestWorker(self.engine, payload)
        self.worker.finished.connect(self._on_backtest_success)
        self.worker.error.connect(self._on_backtest_error)
        self.worker.start()

    def _on_backtest_success(self, result: dict):
        self.sidebar.btn_run.setEnabled(True)
        self.sidebar.btn_run.setText("▶ Run Backtest")
        self.status_bar.showMessage(f"Completed backtest for {result['ticker']} successfully.")

        strat_res = result["strategy_result"]
        bench_res = result["benchmark_result"]
        strat_metrics = strat_res["metrics"]
        bench_metrics = bench_res["metrics"]
        currency = result.get("currency", "$")
        initial_capital = result.get("initial_capital", 10000.0)

        # 1. Update KPI Cards
        strat_return = strat_metrics.get("Total Return (%)", 0.0)
        bench_return = bench_metrics.get("Total Return (%)", 0.0)
        delta_return = strat_return - bench_return

        self.kpi_return.set_value(
            value=f"{strat_return:+.2f}%",
            sub_text=f"vs Bench {bench_return:+.1f}% ({delta_return:+.1f}%)",
            is_positive=(strat_return >= 0)
        )

        cagr = strat_metrics.get("CAGR (%)", 0.0)
        self.kpi_cagr.set_value(
            value=f"{cagr:+.2f}%",
            sub_text="Annualized Growth",
            is_positive=(cagr >= 0)
        )

        mdd = strat_metrics.get("Max Drawdown (%)", 0.0)
        self.kpi_mdd.set_value(
            value=f"{mdd:.2f}%",
            sub_text="Peak-to-Trough Decline",
            is_positive=(mdd > -15.0)
        )

        balance = strat_metrics.get("Final Balance", 0.0)
        self.kpi_balance.set_value(
            value=f"{currency}{balance:,.2f}",
            sub_text=f"From {currency}{initial_capital:,.2f}",
            is_positive=(balance >= initial_capital)
        )

        # 2. Update Charts
        trade_events = strat_res.get("trade_events", [])
        self.chart_view.plot_results(
            strat_df=strat_res["df"],
            bench_df=bench_res["df"],
            trade_events=trade_events,
            currency=currency
        )

        # 3. Update Trade Activity Table & Count
        self.trade_table.load_trades(trade_events, currency=currency)
        self.lbl_trade_count.setText(f"{len(trade_events)} trades")

    def _on_backtest_error(self, err_msg: str):
        self.sidebar.btn_run.setEnabled(True)
        self.sidebar.btn_run.setText("▶ Run Backtest")
        self.chart_view.hide_loading()
        self.status_bar.showMessage(f"Error: {err_msg}")
        QMessageBox.warning(self, "Backtest Error", f"Unable to run backtest:\n\n{err_msg}")

    def _start_comparison(self, payload: dict):
        if self.is_comparing or (self.comp_worker and self.comp_worker.isRunning()):
            return

        ticker = payload["ticker"]
        self.is_comparing = True
        self.status_bar.showMessage(f"Running all 5 strategies on {ticker} for comparison...")
        self.comparison_view.show_loading(f"Simulating all 5 strategies on {ticker}...")

        self.comp_worker = ComparisonWorker(self.engine, payload)
        self.comp_worker.finished.connect(self._on_comparison_success)
        self.comp_worker.error.connect(self._on_comparison_error)
        self.comp_worker.start()

    def _on_comparison_success(self, result: dict):
        self.is_comparing = False
        payload = self.sidebar.get_current_payload()
        self.last_compared_key = (result.get("ticker"), payload["start_date"], payload["capital"])
        self.status_bar.showMessage(f"Successfully compared and ranked all 5 strategies for {result['ticker']}.")

        self.comparison_view.update_comparison_data(result)

    def _on_comparison_error(self, err_msg: str):
        self.is_comparing = False
        self.comparison_view.hide_loading()
        self.status_bar.showMessage(f"Comparison Error: {err_msg}")
        QMessageBox.warning(self, "Comparison Error", f"Unable to compare strategies:\n\n{err_msg}")

