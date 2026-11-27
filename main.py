"""
main.py - Root entry point for QuantSim (Stock Market Strategy Backtester).
Assembled by all 4 team members: Shourya (UI), Rounak (Strategies), Prakshat (APIs), Naman (Backend & Bridge).
"""

import sys  # System path and interpreter utilities
import os  # Filesystem path resolution

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))  # Resolve root project folder (StockBackTest/)
if ROOT_DIR not in sys.path:  # Ensure Shourya/, Rounak/, Prakshat/, Naman/ packages are importable from anywhere
    sys.path.insert(0, ROOT_DIR)  # Prepend project root to Python module search path

from Naman.app import launch_app  # Import Naman's master application launcher that bridges all 4 modules

if __name__ == "__main__":  # Run GUI only when main.py is executed directly
    launch_app()  # Start the PySide6 desktop application
