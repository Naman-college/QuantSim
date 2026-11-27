"""
tests/test_api.py - End-to-end tests for Naman's FastAPI endpoints, Prakshat's serializers, and Shourya's built UI.
"""

import sys  # Python path setup
import os  # Path utilities

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Project root folder
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from fastapi.testclient import TestClient  # FastAPI synchronous test client
from Naman.api import app  # FastAPI application instance

client = TestClient(app)  # Instantiate test client


def test_health_and_static_ui():
    """Verifies /api/health and that Shourya/dist/index.html is served at root '/'."""
    health = client.get("/api/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"
    assert health.json()["strategies"] == 5

    root = client.get("/")
    assert root.status_code == 200
    assert "QuantSim" in root.text


def test_search_and_presets():
    """Verifies Prakshat's stock search and market presets endpoints."""
    res = client.get("/api/search?q=Reliance&limit=5")
    assert res.status_code == 200
    symbols = [item["symbol"] for item in res.json()["results"]]
    assert "RELIANCE.NS" in symbols

    presets = client.get("/api/presets")
    assert presets.status_code == 200
    assert "US Equities & ETFs" in presets.json()["presets"]


def test_backtest_endpoint_and_indian_currency():
    """Verifies POST /api/backtest returns chart-ready JSON and '₹' for NSE stocks."""
    resp = client.post("/api/backtest", json={
        "ticker": "RELIANCE.NS",
        "strategy_name": "5. Moving Average Crossover",
        "start_date": "2023-01-01",
        "initial_capital": 100000.0,
        "strategy_params": {
            "fast_period": 10,
            "slow_period": 30,
            "ma_type": "EMA",
            "use_trend_filter": True
        }
    })
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["currency"] == "₹"
    assert len(payload["charts"]["equityData"]) > 10
    assert len(payload["charts"]["candleData"]) > 10
    assert len(payload["charts"]["indicators"]["maFast"]) > 10


def test_compare_endpoint():
    """Verifies POST /api/compare runs all 5 strategies and returns ranked leaderboard rows."""
    resp = client.post("/api/compare", json={
        "ticker": "SPY",
        "start_date": "2023-01-01",
        "initial_capital": 10000.0,
        "strategy_params_dict": {}
    })
    assert resp.status_code == 200
    payload = resp.json()
    assert len(payload["ranking"]) == 5
    assert len(payload["lines"]) == 5
    assert payload["ranking"][0]["rank"] == 1
