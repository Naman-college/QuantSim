"""
sidebar.py - Modern Linear.app-styled Sidebar with Unified Stock Search & Add.
Maintained by Member 4 (UI/UX Developer).
"""

from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QLabel, QComboBox, QLineEdit,
    QPushButton, QSpinBox, QDoubleSpinBox, QDateEdit,
    QStackedWidget, QWidget, QFormLayout, QHBoxLayout,
    QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt, QDate, Signal, QTimer, QThread
from strategies import AVAILABLE_STRATEGIES
from core.stock_search import search_stocks
from config.presets import get_currency_symbol
from config.theme import (
    COLOR_SURFACE, COLOR_SURFACE_ELEVATED, COLOR_BORDER,
    COLOR_BORDER_FOCUS, COLOR_ACCENT, COLOR_ACCENT_HOVER,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_SUCCESS
)


class StockSearchWorker(QThread):
    """Asynchronous worker for querying stock tickers without lagging the UI."""
    results_ready = Signal(list)

    def __init__(self, query: str):
        super().__init__()
        self.query = query

    def run(self):
        matches = search_stocks(self.query, limit=10)
        self.results_ready.emit(matches)


class Sidebar(QFrame):
    """
    Sleek control sidebar featuring:
    1. Search & Select stock with instant dropdown suggestions
    2. Selected stock status badge (with active exchange & market tag)
    3. Strategy selection & simplified parameters
    4. Capital & Date timeframe controls
    5. Action buttons: 'Run Backtest' & 'Compare All Strategies'
    """
    run_backtest_signal = Signal(dict)
    stock_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebarPanel")
        self.setMinimumWidth(260)
        self.setMaximumWidth(420)

        self.selected_symbol = "SPY"
        self.selected_name = "SPDR S&P 500 ETF Trust"
        self.search_worker = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # 1. Header with Linear Branding
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)
        status_dot = QLabel("●")
        status_dot.setStyleSheet(f"color: {COLOR_SUCCESS}; font-size: 11px;")
        header_layout.addWidget(status_dot)

        app_title = QLabel("QUANTSIM")
        app_title.setStyleSheet("font-size: 13px; font-weight: 800; letter-spacing: 1.5px; color: #FFFFFF;")
        header_layout.addWidget(app_title)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # 2. Stock Search & Add Section
        layout.addWidget(self._create_header("STOCK / ASSET SEARCH"))

        search_box_layout = QVBoxLayout()
        search_box_layout.setSpacing(4)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Search ticker or company (e.g. NVDA, Tata, SPY)...")
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLOR_SURFACE_ELEVATED};
                border: 1px solid {COLOR_BORDER};
                border-radius: 6px;
                padding: 7px 10px;
                color: {COLOR_TEXT_PRIMARY};
                font-size: 12px;
            }}
            QLineEdit:focus {{
                border: 1px solid {COLOR_ACCENT};
            }}
        """)
        search_box_layout.addWidget(self.search_input)

        # Search Suggestions Dropdown List (hidden by default)
        self.results_list = QListWidget()
        self.results_list.setFixedHeight(140)
        self.results_list.hide()
        self.results_list.setStyleSheet(f"""
            QListWidget {{
                background-color: #14161C;
                border: 1px solid {COLOR_BORDER_FOCUS};
                border-radius: 6px;
                color: {COLOR_TEXT_PRIMARY};
                font-size: 11px;
                outline: none;
                padding: 2px;
            }}
            QListWidget::item {{
                padding: 6px 8px;
                border-bottom: 1px solid #1C1E26;
                border-radius: 4px;
            }}
            QListWidget::item:hover {{
                background-color: #1F222C;
                color: #FFFFFF;
            }}
            QListWidget::item:selected {{
                background-color: {COLOR_ACCENT};
                color: #FFFFFF;
            }}
        """)
        search_box_layout.addWidget(self.results_list)
        layout.addLayout(search_box_layout)

        # Debounced Search Timer
        self.search_timer = QTimer(self)
        self.search_timer.setSingleShot(True)
        self.search_timer.setInterval(220)
        self.search_timer.timeout.connect(self._trigger_search)
        self.search_input.textChanged.connect(self.search_timer.start)
        self.results_list.itemClicked.connect(self._on_search_item_clicked)

        # Active Selected Stock Pill / Card
        self.active_stock_card = QFrame()
        self.active_stock_card.setStyleSheet(f"""
            QFrame {{
                background-color: #161820;
                border: 1px solid {COLOR_BORDER};
                border-radius: 6px;
                padding: 6px 8px;
            }}
        """)
        stock_card_layout = QHBoxLayout(self.active_stock_card)
        stock_card_layout.setContentsMargins(6, 4, 6, 4)
        stock_card_layout.setSpacing(6)

        self.lbl_selected_sym = QLabel("SPY")
        self.lbl_selected_sym.setStyleSheet("font-family: 'JetBrains Mono', monospace; font-size: 13px; font-weight: 700; color: #FFFFFF;")
        stock_card_layout.addWidget(self.lbl_selected_sym)

        self.lbl_selected_name = QLabel("S&P 500 ETF")
        self.lbl_selected_name.setStyleSheet(f"font-size: 11px; color: {COLOR_TEXT_SECONDARY};")
        stock_card_layout.addWidget(self.lbl_selected_name, stretch=1)

        self.lbl_currency_tag = QLabel("$ USD")
        self.lbl_currency_tag.setStyleSheet(f"""
            background-color: rgba(94, 106, 210, 0.15);
            color: {COLOR_ACCENT};
            border: 1px solid rgba(94, 106, 210, 0.3);
            border-radius: 4px;
            font-size: 10px;
            font-weight: 600;
            padding: 2px 5px;
        """)
        stock_card_layout.addWidget(self.lbl_currency_tag)
        layout.addWidget(self.active_stock_card)

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

        # 6. Action Button
        self.btn_run = QPushButton("▶ Run Backtest")
        self.btn_run.setObjectName("primaryButton")
        self.btn_run.setCursor(Qt.PointingHandCursor)
        self.btn_run.setFixedHeight(38)
        self.btn_run.clicked.connect(self._emit_run)
        layout.addWidget(self.btn_run)

        self._update_currency_display()

    def _trigger_search(self):
        query = self.search_input.text().strip()
        if not query:
            self.results_list.hide()
            return

        if self.search_worker and self.search_worker.isRunning():
            self.search_worker.terminate()
            self.search_worker.wait()

        self.search_worker = StockSearchWorker(query)
        self.search_worker.results_ready.connect(self._populate_search_results)
        self.search_worker.start()

    def _populate_search_results(self, matches: list):
        self.results_list.clear()
        if not matches:
            self.results_list.hide()
            return

        for item in matches:
            sym = item["symbol"]
            name = item["name"]
            market = item.get("market", "")
            
            # Formatted list item
            list_item = QListWidgetItem(f"{sym}  —  {name} ({market})")
            list_item.setData(Qt.UserRole, item)
            self.results_list.addItem(list_item)

        self.results_list.show()

    def _on_search_item_clicked(self, item: QListWidgetItem):
        data = item.data(Qt.UserRole)
        if data:
            self.selected_symbol = data["symbol"]
            self.selected_name = data["name"]
            self.lbl_selected_sym.setText(self.selected_symbol)
            self.lbl_selected_name.setText(self.selected_name[:24] + "..." if len(self.selected_name) > 24 else self.selected_name)
            
            self._update_currency_display()
            self.search_input.clear()
            self.results_list.hide()
            self.stock_changed.emit(self.selected_symbol)

    def _update_currency_display(self):
        sym = get_currency_symbol(self.selected_symbol)
        is_in = "Rs" in sym
        self.lbl_currency_tag.setText("₹ INR" if is_in else "$ USD")
        self.lbl_currency_tag.setStyleSheet(f"""
            background-color: rgba(94, 106, 210, 0.15);
            color: {COLOR_ACCENT};
            border: 1px solid rgba(94, 106, 210, 0.3);
            border-radius: 4px;
            font-size: 10px;
            font-weight: 600;
            padding: 2px 6px;
        """)
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

    def _collect_payload(self) -> dict:
        ticker = self.selected_symbol.upper()
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

        # Build full strategy parameters dict for multi-strategy comparison
        all_params_dict = {
            "1. Lump Sum Investment": {},
            "2. Buying Dips": {"dip_pct": float(self.spin_dip_pct.value())},
            "3. SIP (Systematic Investment Plan)": {"monthly_installment": float(self.spin_sip_amount.value())},
            "4. Target Gain & Stop Loss": {
                "target_gain_pct": float(self.spin_target_gain.value()),
                "stop_loss_pct": float(self.spin_stop_loss.value()),
            },
            "5. Moving Average Crossover": {
                "fast_period": int(self.spin_ma_fast.value()),
                "slow_period": int(self.spin_ma_slow.value()),
            }
        }

        return {
            "ticker": ticker,
            "strategy_name": strat_name,
            "start_date": start_date,
            "capital": capital,
            "params": params,
            "all_params": all_params_dict
        }

    def get_current_payload(self) -> dict:
        return self._collect_payload()

    def _emit_run(self):
        self.run_backtest_signal.emit(self._collect_payload())
