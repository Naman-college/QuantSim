"""
trade_table.py - Linear-styled Trade Activity Log for the right-hand panel.
Maintained by Member 4 (UI/UX Developer).
"""

from PySide6.QtWidgets import (
    QTableWidget, QTableWidgetItem, QHeaderView, QWidget,
    QHBoxLayout, QLabel
)
from PySide6.QtCore import Qt
from config.theme import (
    COLOR_SURFACE, COLOR_BORDER, COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY, COLOR_SUCCESS, COLOR_DANGER
)


class TradeTable(QTableWidget):
    """
    Vertical trade activity log optimized for the right-hand dashboard panel.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(3)
        self.setHorizontalHeaderLabels(["DATE", "ACTION", "PRICE"])
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.verticalHeader().setVisible(False)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setAlternatingRowColors(True)
        self.setStyleSheet(f"""
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

    def load_trades(self, trade_events: list, currency: str = "$"):
        """Populates the table with trade events: [(date, price, action_str), ...]"""
        self.setRowCount(0)
        self.setRowCount(len(trade_events))

        for row, event in enumerate(reversed(trade_events)):
            date, price, action = event
            date_str = str(date)[:10]

            # 1. Date
            item_date = QTableWidgetItem(date_str)
            item_date.setForeground(Qt.GlobalColor.gray)
            self.setItem(row, 0, item_date)

            # 2. Action Badge
            is_buy = "BUY" in action.upper()
            action_badge = QLabel(f" {action} ")
            badge_color = COLOR_SUCCESS if is_buy else COLOR_DANGER
            action_badge.setStyleSheet(f"""
                color: {badge_color};
                background-color: rgba({int(badge_color[1:3], 16)}, {int(badge_color[3:5], 16)}, {int(badge_color[5:7], 16)}, 0.15);
                border-radius: 4px;
                font-size: 11px;
                font-weight: 700;
                padding: 2px 6px;
            """)
            action_container = QWidget()
            layout = QHBoxLayout(action_container)
            layout.setContentsMargins(2, 2, 2, 2)
            layout.addWidget(action_badge)
            layout.addStretch()
            self.setCellWidget(row, 1, action_container)

            # 3. Price
            item_price = QTableWidgetItem(f"{currency}{float(price):,.2f}")
            item_price.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.setItem(row, 2, item_price)
