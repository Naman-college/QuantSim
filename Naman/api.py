"""
Naman/api.py - FastAPI Backend Server Bridging Finance APIs, Strategies, Metrics & ShadCN UI.
Member: Naman (Backend and Bridging Everyone's Work to Complete the Final App).

Exposes REST endpoints consumed by Shourya's ShadCN React UI and serves the compiled
Shourya/dist/ static bundle so the full app works 100% offline.
"""

import os  # Filesystem path resolution for Shourya/dist static assets
from typing import Dict, Any, Optional  # Type hints for Pydantic request schemas
from fastapi import FastAPI, HTTPException, Query  # FastAPI router, HTTP error responses, and query validation
from fastapi.staticfiles import StaticFiles  # Serves compiled React/ShadCN JS/CSS/HTML files
from fastapi.responses import FileResponse  # Serves index.html for root route
from pydantic import BaseModel, Field  # Request payload validation models

from Naman.engine import BacktestEngine  # Core backtest coordinator (Naman)
from Prakshat.stock_search import search_stocks, CURATED_WATCHLIST  # Hybrid search & 100+ offline watchlist (Prakshat)
from Prakshat.presets import PRESET_MARKETS  # Curated market watchlists (Prakshat)
from Prakshat.chart_serializer import serialize_single_backtest, serialize_comparison_result  # Chart JSON serializers (Prakshat)
from Rounak import AVAILABLE_STRATEGIES  # Registered 5 trading strategies (Rounak)

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Project root (StockBackTest/)
DIST_DIR = os.path.join(ROOT_DIR, "Shourya", "dist")  # Compiled Vite + ShadCN production bundle folder

app = FastAPI(title="QuantSim API", version="2.0.0")  # Instantiate FastAPI application
engine = BacktestEngine()  # Create shared BacktestEngine instance


class BacktestRequest(BaseModel):
    """Validated JSON body for POST /api/backtest."""
    ticker: str = Field(..., min_length=1, description="Stock or ETF ticker symbol")  # Required ticker
    strategy_name: str = Field(..., min_length=1, description="Registered strategy name")  # Required strategy
    start_date: str = Field(default="2020-01-01", description="ISO start date YYYY-MM-DD")  # Start date
    end_date: Optional[str] = Field(default=None, description="Optional ISO end date")  # End date
    initial_capital: float = Field(default=10000.0, gt=0, description="Starting portfolio cash")  # Positive capital
    strategy_params: Dict[str, Any] = Field(default_factory=dict, description="Strategy hyperparameters")  # Params dict


class CompareRequest(BaseModel):
    """Validated JSON body for POST /api/compare."""
    ticker: str = Field(..., min_length=1)  # Required ticker symbol
    start_date: str = Field(default="2020-01-01")  # Backtest start date
    end_date: Optional[str] = Field(default=None)  # Optional end date
    initial_capital: float = Field(default=10000.0, gt=0)  # Starting capital
    strategy_params_dict: Dict[str, Dict[str, Any]] = Field(default_factory=dict)  # Per-strategy parameters map


@app.get("/api/health")
def health_check():
    """Lightweight health check polled by Naman/app.py before opening the desktop window."""
    return {"status": "ok", "strategies": len(AVAILABLE_STRATEGIES)}  # Return status and strategy count


@app.get("/api/strategies")
def list_strategies():
    """Returns metadata for Rounak's 5 trading strategies."""
    return {
        "strategies": [
            {"name": name, "description": strat.description}  # Serialize name and description
            for name, strat in AVAILABLE_STRATEGIES.items()
        ]
    }


@app.get("/api/presets")
def list_presets():
    """Returns Prakshat's curated US & Indian market presets."""
    return {"presets": PRESET_MARKETS}


@app.get("/api/watchlist")
def list_watchlist():
    """Returns Prakshat's full 100+ curated watchlist for 0ms instant client-side filtering."""
    return {"results": CURATED_WATCHLIST}


@app.get("/api/search")
def api_search_stocks(q: str = Query(default=""), limit: int = Query(default=12, ge=1, le=25)):
    """Searches Prakshat's offline watchlist and live Yahoo Finance autocomplete API."""
    results = search_stocks(query=q, limit=limit)  # Delegate to Prakshat's hybrid search
    return {"results": results}  # Return standardized match array


@app.post("/api/backtest")
def api_run_backtest(req: BacktestRequest):
    """Executes one selected strategy via BacktestEngine and returns chart-ready JSON."""
    try:
        raw_result = engine.run_backtest(  # Run strategy + Buy & Hold benchmark
            ticker=req.ticker.strip().upper(),
            strategy_name=req.strategy_name,
            start_date=req.start_date,
            end_date=req.end_date,
            initial_capital=req.initial_capital,
            strategy_params=req.strategy_params,
        )
        return serialize_single_backtest(raw_result)  # Format DataFrames via Prakshat's serializer
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))  # Surface validation/data errors cleanly to UI toast
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backtest error: {e}")  # Catch unexpected server errors


@app.post("/api/compare")
def api_compare_strategies(req: CompareRequest):
    """Runs all 5 strategies simultaneously and returns ranked leaderboard + 5-line overlay JSON."""
    try:
        raw_result = engine.run_all_strategies(  # Execute and rank all 5 strategies
            ticker=req.ticker.strip().upper(),
            start_date=req.start_date,
            end_date=req.end_date,
            initial_capital=req.initial_capital,
            strategy_params_dict=req.strategy_params_dict,
        )
        return serialize_comparison_result(raw_result)  # Serialize overlay curves and leaderboard rows
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))  # Client error status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison error: {e}")  # Server error status


if os.path.isdir(os.path.join(DIST_DIR, "assets")):  # Mount Vite JS/CSS assets directory if built
    app.mount(
        "/assets",
        StaticFiles(directory=os.path.join(DIST_DIR, "assets")),
        name="assets",
    )


@app.get("/")
def serve_index():
    """Serves the compiled ShadCN React index.html at root URL."""
    index_path = os.path.join(DIST_DIR, "index.html")  # Path to Vite build output
    if not os.path.isfile(index_path):  # Helpful error if ShadCN UI hasn't been built yet
        raise HTTPException(
            status_code=503,
            detail="ShadCN UI bundle not found. Run 'npm run build' inside Shourya/ first.",
        )
    return FileResponse(index_path)  # Return compiled HTML page
