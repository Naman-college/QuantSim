"""
main_window.py - Main Window with 3-column layout (Sidebar | Chart & KPIs | Right Trade Panel).
Maintained by Member 4 (UI/UX Developer).
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QMessageBox, QLabel, QStatusBar, QFrame
)
from PySide6.QtCore import Qt, QThread, Signal
from ui.components.sidebar import Sidebar
from ui.components.kpi_card import KPICard
from ui.components.chart_view import ChartView
from ui.components.trade_table import TradeTable
from core.engine import BacktestEngine
from config.theme import (
    COLOR_CANVAS, COLOR_SURFACE, COLOR_BORDER,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY
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


class MainWindow(QMainWindow):
    """
    Main Application Window featuring a 3-column layout:
    - Column 1 (Left): Minimalist Sidebar
    - Column 2 (Center): 4 KPI Metric Cards & TradingView Chart
    - Column 3 (Right): Full-height Trade Activity Log
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stock Market Strategy Backtester — Linear Theme")
        self.resize(1340, 840)
        self.engine = BacktestEngine()
        self.worker = None

        self._setup_ui()

        # Initial backtest on startup
        self.sidebar._emit_run()

    def _setup_ui(self):
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)

        # ----------------------------------------------------
        # 1. Left Column: Control Sidebar (~290px)
        # ----------------------------------------------------
        self.sidebar = Sidebar()
        self.sidebar.run_backtest_signal.connect(self._start_backtest)
        main_layout.addWidget(self.sidebar)

        # ----------------------------------------------------
        # 2. Center Column: KPI Cards & Full-Height Chart (Stretch 1)
        # ----------------------------------------------------
        center_container = QWidget()
        center_layout = QVBoxLayout(center_container)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(10)

        # KPI Metric Cards (Horizontal Bar)
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

        # TradingView Interactive Chart (Takes full remaining space)
        self.chart_view = ChartView()
        center_layout.addWidget(self.chart_view, stretch=1)

        main_layout.addWidget(center_container, stretch=1)

        # ----------------------------------------------------
        # 3. Right Column: Trade Activity Log (~320px)
        # ----------------------------------------------------
        right_panel = QFrame()
        right_panel.setObjectName("cardPanel")
        right_panel.setFixedWidth(320)
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

        # Header with trade count
        trade_header_layout = QHBoxLayout()
        trade_title = QLabel("TRADE ACTIVITY LOG")
        trade_title.setObjectName("sectionHeader")
        trade_header_layout.addWidget(trade_title)

        self.lbl_trade_count = QLabel("0 trades")
        self.lbl_trade_count.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 11px;")
        trade_header_layout.addStretch()
        trade_header_layout.addWidget(self.lbl_trade_count)
        right_layout.addLayout(trade_header_layout)

        # Vertical Trade Table
        self.trade_table = TradeTable()
        right_layout.addWidget(self.trade_table, stretch=1)

        main_layout.addWidget(right_panel)

        self.setCentralWidget(central_widget)

        # Minimalist Status Bar
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet(f"background-color: {COLOR_SURFACE}; color: {COLOR_TEXT_SECONDARY}; border-top: 1px solid {COLOR_BORDER};")
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready. Select parameters and click 'Run Backtest'.")

    def _start_backtest(self, payload: dict):
        ticker = payload["ticker"]
        strat = payload["strategy_name"]
        self.status_bar.showMessage(f"Fetching data and calculating backtest for {ticker} ({strat})...")
        self.sidebar.btn_run.setEnabled(False)
        self.sidebar.btn_run.setText("Calculating...")

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
        self.status_bar.showMessage(f"Error: {err_msg}")
        QMessageBox.warning(self, "Backtest Error", f"Unable to run backtest:\n\n{err_msg}")
