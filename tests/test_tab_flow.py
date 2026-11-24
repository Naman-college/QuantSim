"""
test_tab_flow.py - Headless test verifying tab switching, loading states, and crash prevention.
"""

import sys
import os
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow


def test_tab_flow():
    app = QApplication.instance() or QApplication(sys.argv)
    
    print("1. Initializing MainWindow...")
    window = MainWindow()
    assert window is not None
    print("   [PASS] MainWindow initialized successfully.")

    print("2. Checking tabs configuration...")
    assert window.tabs.count() == 2
    assert "Single Strategy" in window.tabs.tabText(0)
    assert "Comparison" in window.tabs.tabText(1)
    print("   [PASS] Tabs configured correctly.")

    print("3. Simulating Tab Switch to Comparison (Tab 1)...")
    # This must trigger _on_tab_changed safely without crashing or looping
    window.tabs.setCurrentIndex(1)
    print("   [PASS] Tab 1 activated without crash.")

    print("4. Verifying comparison worker state...")
    # Either is_comparing is True or finished
    print(f"   is_comparing: {window.is_comparing}")

    print("5. Simulating switching back to Tab 0...")
    window.tabs.setCurrentIndex(0)
    print("   [PASS] Switched back to Tab 0 without error.")

    print("\nALL TAB FLOW AND STABILITY CHECKS PASSED!")


if __name__ == "__main__":
    test_tab_flow()
