"""
main.py - Entry point for the Linear-styled Stock Market Strategy Backtester.
Semester 3 Python Project (NumPy & pandas).
"""

import sys
import os

# Ensure project root is in python path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from ui.main_window import MainWindow
from config.theme import LINEAR_STYLESHEET


def main():
    # Enable High DPI pixmaps
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("Linear Stock Backtester")
    # Set default font point size so internal Qt widgets don't see pointSize -1
    app.setFont(QFont("Segoe UI", 10))
    
    # Apply Linear.app dark theme stylesheet
    app.setStyleSheet(LINEAR_STYLESHEET)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
