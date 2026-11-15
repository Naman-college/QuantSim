"""
kpi_card.py - Linear.app-styled KPI Metric Card widget.
Maintained by Member 4 (UI/UX Developer).
"""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QHBoxLayout
from PySide6.QtCore import Qt
from config.theme import (
    COLOR_SURFACE, COLOR_BORDER, COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY, COLOR_SUCCESS, COLOR_DANGER
)


class KPICard(QFrame):
    """
    A minimalist metric display card inspired by Linear.app.
    Shows Title, Primary Value (tabular font), and Subtitle/Benchmark delta.
    """
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setObjectName("cardPanel")
        self.setStyleSheet(f"""
            QFrame#cardPanel {{
                background-color: {COLOR_SURFACE};
                border: 1px solid {COLOR_BORDER};
                border-radius: 6px;
                padding: 12px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(4)

        # Title Label (Small, muted uppercase)
        self.lbl_title = QLabel(title.upper())
        self.lbl_title.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 11px; font-weight: 600; letter-spacing: 0.5px;")
        layout.addWidget(self.lbl_title)

        # Primary Value Label (Big, bold, monospace)
        self.lbl_value = QLabel("—")
        self.lbl_value.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-size: 20px; font-weight: 700; font-family: 'JetBrains Mono', 'Consolas', monospace;")
        layout.addWidget(self.lbl_value)

        # Subtitle / Delta pill
        self.lbl_sub = QLabel("—")
        self.lbl_sub.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 11px;")
        layout.addWidget(self.lbl_sub)

    def set_value(self, value: str, sub_text: str = "", is_positive: bool = None):
        """Updates the card value with optional positive/negative styling."""
        self.lbl_value.setText(value)
        self.lbl_sub.setText(sub_text)

        if is_positive is True:
            self.lbl_value.setStyleSheet(f"color: {COLOR_SUCCESS}; font-size: 20px; font-weight: 700; font-family: 'JetBrains Mono', 'Consolas', monospace;")
        elif is_positive is False:
            self.lbl_value.setStyleSheet(f"color: {COLOR_DANGER}; font-size: 20px; font-weight: 700; font-family: 'JetBrains Mono', 'Consolas', monospace;")
        else:
            self.lbl_value.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-size: 20px; font-weight: 700; font-family: 'JetBrains Mono', 'Consolas', monospace;")
