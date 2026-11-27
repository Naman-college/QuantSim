"""
Prakshat/chart_serializer.py - Converts pandas backtest DataFrames into JSON payloads for TradingView Charts API.
Member: Prakshat (Finance API and Charts API Integration).
"""

from typing import Dict, Any, List  # Type annotations for serialized chart payloads
import pandas as pd  # DataFrame inspection and NaN filtering

# Consistent ShadCN/TradingView color palette for the 5-strategy comparison chart
STRATEGY_COLORS: Dict[str, str] = {
    "1. Lump Sum Investment": "#71717A",            # Zinc-500 dashed baseline
    "2. Buying Dips": "#10B981",                    # Emerald-500
    "3. SIP (Systematic Investment Plan)": "#38BDF8", # Sky-400
    "4. Target Gain & Stop Loss": "#F59E0B",        # Amber-500
    "5. Moving Average Crossover": "#6366F1",       # Indigo-500
}


def serialize_single_backtest(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Serializes BacktestEngine.run_backtest() output into clean JSON for FastAPI & Lightweight Charts.
    """
    strat_res = result["strategy_result"]  # Selected strategy DataFrame, metrics, trade_events, params
    bench_res = result["benchmark_result"]  # Buy & Hold benchmark DataFrame and metrics
    strat_df: pd.DataFrame = strat_res["df"]  # Annotated strategy DataFrame
    bench_df: pd.DataFrame = bench_res["df"]  # Annotated benchmark DataFrame

    equity_data: List[Dict[str, Any]] = []  # Strategy equity time series [{time, value}]
    candle_data: List[Dict[str, Any]] = []  # OHLC candlestick bars [{time, open, high, low, close}]
    drawdown_data: List[Dict[str, Any]] = []  # Underwater drawdown % series [{time, value}]
    ma_fast_data: List[Dict[str, Any]] = []  # Optional Fast SMA/EMA overlay
    ma_slow_data: List[Dict[str, Any]] = []  # Optional Slow SMA/EMA overlay
    ma_trend_data: List[Dict[str, Any]] = []  # Optional 200-SMA macro trend filter overlay

    has_ma_fast = "MA_Fast" in strat_df.columns  # Check if strategy computed Fast MA
    has_ma_slow = "MA_Slow" in strat_df.columns  # Check if strategy computed Slow MA
    has_ma_trend = "MA_Trend" in strat_df.columns  # Check if strategy computed Trend MA

    for dt, row in strat_df.iterrows():  # Single pass over strategy DataFrame for O(N) serialization
        date_str = str(dt)[:10]  # Format DatetimeIndex row as 'YYYY-MM-DD'
        close_val = float(row["Close"])  # Mandatory Close price
        open_val = float(row["Open"]) if "Open" in row else close_val  # Open price fallback
        high_val = float(row["High"]) if "High" in row else max(open_val, close_val)  # High price fallback
        low_val = float(row["Low"]) if "Low" in row else min(open_val, close_val)  # Low price fallback
        eq_val = float(row["Equity"]) if "Equity" in row else result.get("initial_capital", 10000.0)  # Portfolio equity
        dd_val = float(row["Drawdown"]) if "Drawdown" in row else 0.0  # Underwater drawdown %

        equity_data.append({"time": date_str, "value": round(eq_val, 2)})  # Append equity point
        drawdown_data.append({"time": date_str, "value": round(dd_val, 2)})  # Append drawdown point
        candle_data.append({  # Append candlestick bar
            "time": date_str,
            "open": round(open_val, 2),
            "high": round(high_val, 2),
            "low": round(low_val, 2),
            "close": round(close_val, 2),
        })

        if has_ma_fast and pd.notna(row["MA_Fast"]):  # Append Fast MA if valid
            ma_fast_data.append({"time": date_str, "value": round(float(row["MA_Fast"]), 2)})
        if has_ma_slow and pd.notna(row["MA_Slow"]):  # Append Slow MA if valid
            ma_slow_data.append({"time": date_str, "value": round(float(row["MA_Slow"]), 2)})
        if has_ma_trend and pd.notna(row["MA_Trend"]):  # Append Trend MA if valid
            ma_trend_data.append({"time": date_str, "value": round(float(row["MA_Trend"]), 2)})

    benchmark_data: List[Dict[str, Any]] = []  # Benchmark equity series [{time, value}]
    if bench_df is not None and not bench_df.empty:  # Populate benchmark points
        for dt, row in bench_df.iterrows():  # Iterate benchmark dates
            benchmark_data.append({
                "time": str(dt)[:10],
                "value": round(float(row["Equity"]), 2),
            })

    trade_events: List[Dict[str, Any]] = []  # Formatted trade events for both Chart markers & ShadCN TradeTable
    for dt, price, action in strat_res.get("trade_events", []):  # Convert tuple list into JSON objects
        action_str = str(action)  # Stringify action text
        trade_events.append({
            "time": str(dt)[:10],
            "price": round(float(price), 2),
            "action": action_str,
            "side": "BUY" if "BUY" in action_str.upper() else "SELL",  # Normalized side flag for UI badges
        })

    return {  # Complete JSON-serializable single-strategy response
        "ticker": result["ticker"],
        "currency": result["currency"],
        "strategy_name": result["strategy_name"],
        "initial_capital": result["initial_capital"],
        "metrics": strat_res["metrics"],
        "benchmark_metrics": bench_res["metrics"],
        "params": strat_res.get("params", {}),
        "trade_events": trade_events,
        "charts": {
            "equityData": equity_data,
            "benchmarkData": benchmark_data,
            "candleData": candle_data,
            "drawdownData": drawdown_data,
            "indicators": {
                "maFast": ma_fast_data,
                "maSlow": ma_slow_data,
                "maTrend": ma_trend_data,
            },
        },
    }


def serialize_comparison_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Serializes BacktestEngine.run_all_strategies() output into JSON for the 5-Strategy Comparison tab.
    """
    strat_results = result.get("strategy_results", {})  # Dictionary of all 5 strategy outputs
    lines: List[Dict[str, Any]] = []  # Multi-series curves for ComparisonChart

    for name, res in strat_results.items():  # Serialize each strategy's equity curve
        df = res.get("df")  # Strategy DataFrame
        if df is None or df.empty or "Equity" not in df.columns:  # Skip empty results
            continue

        series_data = [  # Build [{time, value}] list cleanly
            {"time": str(dt)[:10], "value": round(float(row["Equity"]), 2)}
            for dt, row in df.iterrows()
        ]
        lines.append({
            "name": name,
            "color": STRATEGY_COLORS.get(name, "#6366F1"),
            "isBenchmark": "Lump Sum" in name,  # Dashed baseline flag for Buy & Hold
            "data": series_data,
        })

    ranking_rows = []  # Enrich each ranking item with its assigned chart color
    for row in result.get("ranking", []):
        enriched = dict(row)  # Shallow copy ranking row
        enriched["color"] = STRATEGY_COLORS.get(row["strategy"], "#6366F1")  # Attach color dot hex
        ranking_rows.append(enriched)

    return {  # Complete JSON-serializable comparison response
        "ticker": result["ticker"],
        "currency": result["currency"],
        "initial_capital": result["initial_capital"],
        "ranking": ranking_rows,
        "lines": lines,
    }
