"""
tests/test_tab_flow.py - Headless integration test verifying FastAPI server + PySide6 MainWindow launch.
"""

import sys  # System args and path helpers
import os  # Filesystem path utilities

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Resolve project root folder
if ROOT_DIR not in sys.path:  # Ensure member packages are importable
    sys.path.insert(0, ROOT_DIR)  # Prepend root directory

from PySide6.QtWidgets import QApplication  # Qt GUI application container
from Naman.app import MainWindow, _find_free_port, start_backend_server  # Naman's desktop shell & server launcher


def test_tab_flow():
    """Starts Naman's FastAPI backend on a free port and verifies Shourya's ShadCN UI loads in MainWindow."""
    app = QApplication.instance() or QApplication(sys.argv)  # Reuse or create QApplication

    port = _find_free_port(8100)  # Find free local test port
    server = start_backend_server(port)  # Start background Uvicorn server
    url = f"http://127.0.0.1:{port}/"  # Root URL serving Shourya/dist/index.html

    try:
        window = MainWindow(url)  # Initialize native PySide6 desktop shell pointing at FastAPI
        app.processEvents()  # Allow Qt to dispatch initial navigation request
        assert window is not None
        assert "QuantSim" in window.windowTitle()
        assert window.app_url == url
        assert window.web_view.page().requestedUrl().toString().startswith(f"http://127.0.0.1:{port}")
        print("[PASS] MainWindow + FastAPI + ShadCN WebEngine shell initialized cleanly.")
    finally:
        server.should_exit = True  # Stop Uvicorn cleanly so pytest exits without hanging


if __name__ == "__main__":
    test_tab_flow()
