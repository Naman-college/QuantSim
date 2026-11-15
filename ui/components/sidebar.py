"""
sidebar.py - Simplified Linear.app-styled Sidebar.
Maintained by Member 4 (UI/UX Developer).
"""

from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QLabel, QComboBox, QLineEdit,
    QPushButton, QSpinBox, QDoubleSpinBox, QDateEdit,
    QStackedWidget, QWidget, QFormLayout, QHBoxLayout
)
from PySide6.QtCore import Qt, QDate, Signal
from strategies import AVAILABLE_STRATEGIES
from config.theme import (
    COLOR_SURFACE, COLOR_BORDER, COLOR_ACCENT,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_SUCCESS
)

# Clean, curated list of top popular stocks (US & India)
POPULAR_TICKERS = [
    ("S&P 500 ETF (SPY)", "SPY"),
    ("Nasdaq 100 ETF (QQQ)", "QQQ"),
    ("Apple Inc. (AAPL)", "AAPL"),
    ("NVIDIA Corp. (NVDA)", "NVDA"),
    ("Tesla Inc. (TSLA)", "TSLA"),
    ("Microsoft Corp. (MSFT)", "MSFT"),
    ("NIFTY 50 Index", "^NSEI"),
    ("Reliance Industries", "RELIANCE.NS"),
    ("Tata Consultancy (TCS)", "TCS.NS"),
    ("HDFC Bank", "HDFCBANK.NS"),
]


class Sidebar(QFrame):
    """
    Minimalist control sidebar for selecting stock, strategy,
    parameters, timeframe, and triggering backtest.
    """
    run_backtest_signal = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebarPanel")
        self.setFixedWidth(290)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 16, 14, 16)
        layout.setSpacing(12)

        # 1. Header
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)
        status_dot = QLabel("●")
        status_dot.setStyleSheet(f"color: {COLOR_SUCCESS}; font-size: 10px;")
        header_layout.addWidget(status_dot)

        app_title = QLabel("BACKTESTER")
        app_title.setStyleSheet("font-size: 12px; font-weight: 700; letter-spacing: 1px;")
        header_layout.addWidget(app_title)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # 2. Stock Selection
        layout.addWidget(self._create_header("SELECT STOCK / ETF"))
        self.combo_ticker = QComboBox()
        for name, symbol in POPULAR_TICKERS:
            self.combo_ticker.addItem(name, userData=symbol)
        self.combo_ticker.currentIndexChanged.connect(self._update_currency_prefix)
        layout.addWidget(self.combo_ticker)

        # Custom Ticker
        self.txt_custom_ticker = QLineEdit()
        self.txt_custom_ticker.setPlaceholderText("Or custom ticker (e.g. AMZN, BTC-USD)")
        self.txt_custom_ticker.textChanged.connect(self._update_currency_prefix)
        layout.addWidget(self.txt_custom_ticker)

        # 3. Strategy Selection
        layout.addWidget(self._create_header("TRADING STRATEGY"))
        self.combo_strategy = QComboBox()
        for strat_name in AVAILABLE_STRATEGIES.keys():
            self.combo_strategy.addItem(strat_name)
        self.combo_strategy.currentIndexChanged.connect(self._on_strategy_changed)
        layout.addWidget(self.combo_strategy)

        # 4. Strategy Parameters
        layout.addWidget(self._create_header("STRATEGY SETTINGS"))
        self.param_stack = QStackedWidget()
        self._setup_parameters()
        layout.addWidget(self.param_stack)

        # 5. Capital & Timeframe
        layout.addWidget(self._create_header("TIMEFRAME & CAPITAL"))
        form_layout = QFormLayout()
        form_layout.setSpacing(8)

        self.spin_capital = QDoubleSpinBox()
        self.spin_capital.setRange(100.0, 10000000.0)
        self.spin_capital.setValue(10000.0)
        self.spin_capital.setPrefix("$ ")
        self.spin_capital.setSingleStep(500.0)
        form_layout.addRow(QLabel("Capital:"), self.spin_capital)

        self.date_start = QDateEdit()
        self.date_start.setCalendarPopup(True)
        self.date_start.setDate(QDate(2020, 1, 1))
        form_layout.addRow(QLabel("Start Date:"), self.date_start)

        layout.addLayout(form_layout)
        layout.addStretch()

        # 6. Run Button
        self.btn_run = QPushButton("▶ Run Backtest")
        self.btn_run.setObjectName("primaryButton")
        self.btn_run.setCursor(Qt.PointingHandCursor)
        self.btn_run.setFixedHeight(38)
        self.btn_run.clicked.connect(self._emit_run)
        layout.addWidget(self.btn_run)

        self._update_currency_prefix()

    def _update_currency_prefix(self):
        from config.presets import get_currency_symbol
        custom = self.txt_custom_ticker.text().strip()
        ticker = custom if custom else (self.combo_ticker.currentData() or "SPY")
        sym = get_currency_symbol(ticker)
        self.spin_capital.setPrefix(f"{sym}")
        self.spin_sip_amount.setPrefix(f"{sym}")

    def _create_header(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setObjectName("sectionHeader")
        return lbl

    def _setup_parameters(self):
        # 0. Lump Sum
        p0 = QWidget()
        l0 = QVBoxLayout(p0)
        l0.setContentsMargins(0, 2, 0, 2)
        lbl0 = QLabel("Simple Buy & Hold on Day 1.\n(Standard baseline benchmark)")
        lbl0.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 11px;")
        l0.addWidget(lbl0)
        self.param_stack.addWidget(p0)

        # 1. Buying Dips
        p1 = QWidget()
        f1 = QFormLayout(p1)
        f1.setContentsMargins(0, 2, 0, 2)
        self.spin_dip_pct = QDoubleSpinBox()
        self.spin_dip_pct.setRange(0.5, 30.0)
        self.spin_dip_pct.setValue(2.0)
        self.spin_dip_pct.setSuffix(" %")
        f1.addRow(QLabel("Dip Drop:"), self.spin_dip_pct)
        self.param_stack.addWidget(p1)

        # 2. SIP
        p2 = QWidget()
        f2 = QFormLayout(p2)
        f2.setContentsMargins(0, 2, 0, 2)
        self.spin_sip_amount = QDoubleSpinBox()
        self.spin_sip_amount.setRange(10.0, 50000.0)
        self.spin_sip_amount.setValue(500.0)
        self.spin_sip_amount.setPrefix("$ ")
        f2.addRow(QLabel("Monthly Add:"), self.spin_sip_amount)
        self.param_stack.addWidget(p2)

        # 3. Target Gain & Stop Loss
        p3 = QWidget()
        f3 = QFormLayout(p3)
        f3.setContentsMargins(0, 2, 0, 2)
        self.spin_target_gain = QDoubleSpinBox()
        self.spin_target_gain.setRange(0.5, 50.0)
        self.spin_target_gain.setValue(5.0)
        self.spin_target_gain.setSuffix(" %")
        f3.addRow(QLabel("Target Gain:"), self.spin_target_gain)

        self.spin_stop_loss = QDoubleSpinBox()
        self.spin_stop_loss.setRange(0.5, 30.0)
        self.spin_stop_loss.setValue(3.0)
        self.spin_stop_loss.setSuffix(" %")
        f3.addRow(QLabel("Stop Loss:"), self.spin_stop_loss)
        self.param_stack.addWidget(p3)

        # 4. Moving Average Crossover
        p4 = QWidget()
        f4 = QFormLayout(p4)
        f4.setContentsMargins(0, 2, 0, 2)
        self.spin_ma_fast = QSpinBox()
        self.spin_ma_fast.setRange(3, 100)
        self.spin_ma_fast.setValue(20)
        self.spin_ma_fast.setSuffix(" days")
        f4.addRow(QLabel("Fast SMA:"), self.spin_ma_fast)

        self.spin_ma_slow = QSpinBox()
        self.spin_ma_slow.setRange(5, 300)
        self.spin_ma_slow.setValue(50)
        self.spin_ma_slow.setSuffix(" days")
        f4.addRow(QLabel("Slow SMA:"), self.spin_ma_slow)
        self.param_stack.addWidget(p4)

    def _on_strategy_changed(self, idx: int):
        self.param_stack.setCurrentIndex(idx)

    def _emit_run(self):
        custom = self.txt_custom_ticker.text().strip()
        ticker = custom.upper() if custom else (self.combo_ticker.currentData() or "SPY")
        strat_name = self.combo_strategy.currentText()
        start_date = self.date_start.date().toString("yyyy-MM-dd")
        capital = float(self.spin_capital.value())

        params = {}
        idx = self.combo_strategy.currentIndex()
        if idx == 1:
            params = {"dip_pct": float(self.spin_dip_pct.value())}
        elif idx == 2:
            params = {"monthly_installment": float(self.spin_sip_amount.value())}
        elif idx == 3:
            params = {
                "target_gain_pct": float(self.spin_target_gain.value()),
                "stop_loss_pct": float(self.spin_stop_loss.value()),
            }
        elif idx == 4:
            params = {
                "fast_period": int(self.spin_ma_fast.value()),
                "slow_period": int(self.spin_ma_slow.value()),
            }

        self.run_backtest_signal.emit({
            "ticker": ticker,
            "strategy_name": strat_name,
            "start_date": start_date,
            "capital": capital,
            "params": params
        })
