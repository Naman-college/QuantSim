"""
Naman/app.py - Native PySide6 Desktop Shell + Embedded Uvicorn FastAPI Server.
Member: Naman (Backend and Bridging Everyone's Work to Complete the Final App).

Starts Naman's FastAPI backend on localhost in a background thread and opens Shourya's
ShadCN UI + Prakshat's TradingView Charts inside a native PySide6 desktop window
(or opens in the default web browser when passed `--browser`).
"""

import sys  # CLI args and exit handling
import socket  # Finds a free local TCP port automatically so multiple runs never collide
import threading  # Runs Uvicorn server in background daemon thread
import time  # Brief polling interval while waiting for FastAPI health check
import urllib.request  # Polls /api/health before loading the desktop WebEngine view
import webbrowser  # Optional --browser launch support
import uvicorn  # ASGI server hosting Naman/api.py

from PySide6.QtWidgets import QApplication, QMainWindow  # Native Qt desktop window shell
from PySide6.QtWebEngineWidgets import QWebEngineView  # Embedded Chromium engine rendering the ShadCN React app
from PySide6.QtCore import Qt, QUrl  # High-DPI policy and localhost URL wrapper
from PySide6.QtGui import QColor  # Dark zinc-950 window background color before page paints

from Naman.api import app as fastapi_app  # Import FastAPI instance bridging backend & UI


def _find_free_port(preferred: int = 8000) -> int:
    """Returns `preferred` port if free on 127.0.0.1, otherwise picks an OS-assigned free port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex(("127.0.0.1", preferred)) != 0:  # Port is unused if connect_ex fails
            return preferred
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))  # Bind port 0 so OS assigns an available ephemeral port
        return int(s.getsockname()[1])  # Return assigned port number


def start_backend_server(port: int) -> uvicorn.Server:
    """Starts Uvicorn serving Naman.api:app on a background daemon thread and waits until healthy."""
    config = uvicorn.Config(fastapi_app, host="127.0.0.1", port=port, log_level="warning")  # Quiet server logs
    server = uvicorn.Server(config)  # Create controllable Uvicorn server instance
    thread = threading.Thread(target=server.run, daemon=True)  # Daemon thread auto-stops on app exit
    thread.start()  # Launch FastAPI server asynchronously

    health_url = f"http://127.0.0.1:{port}/api/health"  # Endpoint verifying server readiness
    for _ in range(50):  # Wait up to ~5 seconds for startup
        try:
            with urllib.request.urlopen(health_url, timeout=0.5) as resp:
                if resp.status == 200:  # Server is ready to accept UI requests
                    break
        except Exception:
            time.sleep(0.1)  # Retry after 100ms
    return server  # Return handle for optional clean shutdown


class MainWindow(QMainWindow):
    """
    Native desktop window hosting the ShadCN UI (Shourya) + TradingView Charts (Prakshat)
    served locally from Naman's FastAPI backend.
    """

    def __init__(self, url: str):
        super().__init__()  # Initialize QMainWindow
        self.app_url = url  # Store local FastAPI server URL
        self.setWindowTitle("QuantSim — Quantitative Strategy Backtester")  # Desktop window title
        self.resize(1440, 900)  # Spacious default workstation resolution
        self.setStyleSheet("background-color: #09090B;")  # Zinc-950 background prevents white flash on launch

        self.web_view = QWebEngineView(self)  # Embedded Chromium view
        self.web_view.page().setBackgroundColor(QColor("#09090B"))  # Match ShadCN dark background immediately
        self.web_view.load(QUrl(url))  # Navigate to local FastAPI server URL
        self.setCentralWidget(self.web_view)  # Fill entire window with ShadCN UI


def launch_app():
    """Launches FastAPI backend and opens QuantSim in native desktop window (or browser with --browser)."""
    port = _find_free_port(8000)  # Reserve an open localhost port
    server = start_backend_server(port)  # Start FastAPI + Uvicorn in background thread
    url = f"http://127.0.0.1:{port}/"  # Local URL serving ShadCN UI + /api/*

    if "--browser" in sys.argv:  # Optional web-browser mode for convenient sharing/demoing
        print(f"QuantSim running in browser mode at {url} (Press Ctrl+C to stop)")
        webbrowser.open(url)  # Open default browser tab
        try:
            while True:  # Keep main thread alive while daemon server runs
                time.sleep(0.5)
        except KeyboardInterrupt:
            server.should_exit = True
            return

    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    qt_app = QApplication(sys.argv)  # Initialize Qt desktop runtime
    qt_app.setApplicationName("QuantSim")  # Set application name

    window = MainWindow(url)  # Create native window pointing to FastAPI localhost URL
    window.show()  # Display desktop window

    exit_code = qt_app.exec()  # Run Qt event loop until window closes
    server.should_exit = True  # Signal Uvicorn to shut down cleanly
    sys.exit(exit_code)  # Exit Python process


if __name__ == "__main__":  # Allow running via `python -m Naman.app`
    launch_app()
