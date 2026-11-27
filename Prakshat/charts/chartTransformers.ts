// Prakshat/charts/chartTransformers.ts - Data types & formatting helpers bridging FastAPI JSON to TradingView Lightweight Charts.

export interface TimeValuePoint {
  time: string; // ISO date string 'YYYY-MM-DD' required by TradingView Lightweight Charts
  value: number; // Numeric equity, indicator, or drawdown % value
}

export interface CandleBar {
  time: string; // Trading date 'YYYY-MM-DD'
  open: number; // Daily opening price
  high: number; // Daily high price
  low: number; // Daily low price
  close: number; // Daily closing price
}

export interface TradeEventItem {
  time: string; // Execution date 'YYYY-MM-DD'
  price: number; // Execution fill price
  action: string; // Descriptive action label (e.g. 'BUY (Golden Cross SMA)')
  side: "BUY" | "SELL"; // Normalized trade direction
}

export interface SingleBacktestResponse {
  ticker: string; // Stock ticker symbol (e.g. 'SPY', 'RELIANCE.NS')
  currency: string; // '$' or '₹'
  strategy_name: string; // Selected strategy display name
  initial_capital: number; // Starting portfolio cash
  metrics: Record<string, number>; // Computed KPI dictionary from Naman/metrics.py
  benchmark_metrics: Record<string, number>; // Buy & Hold benchmark KPIs
  params: Record<string, string>; // Formatted parameter summary
  trade_events: TradeEventItem[]; // Chronological BUY/SELL list
  charts: {
    equityData: TimeValuePoint[]; // Strategy equity curve
    benchmarkData: TimeValuePoint[]; // Benchmark equity curve
    candleData: CandleBar[]; // OHLC candlestick bars
    drawdownData: TimeValuePoint[]; // Underwater drawdown % curve
    indicators: {
      maFast: TimeValuePoint[]; // Optional Fast SMA/EMA overlay
      maSlow: TimeValuePoint[]; // Optional Slow SMA/EMA overlay
      maTrend: TimeValuePoint[]; // Optional 200-SMA macro trend filter overlay
    };
  };
}

export interface ComparisonLine {
  name: string; // Strategy name
  color: string; // Assigned hex stroke color
  isBenchmark: boolean; // True for Lump Sum dashed baseline
  data: TimeValuePoint[]; // Equity curve time series
}

export interface ComparisonRankingRow {
  rank: number; // 1-based performance rank
  strategy: string; // Strategy name
  total_return: number; // Total return %
  cagr: number; // Annualized CAGR %
  sharpe: number; // Risk-adjusted Sharpe ratio
  max_drawdown: number; // Maximum peak-to-trough decline %
  final_balance: number; // Ending balance
  trades: number; // Number of trade events
  win_rate: number; // Active-day win rate %
  color: string; // Assigned hex dot color
}

export interface ComparisonResponse {
  ticker: string; // Active asset ticker
  currency: string; // '$' or '₹'
  initial_capital: number; // Starting capital
  ranking: ComparisonRankingRow[]; // Sorted leaderboard rows
  lines: ComparisonLine[]; // 5 equity curves for overlay chart
}

/** Formats currency cleanly using Indian ('en-IN') or US ('en-US') digit grouping. */
export function formatCurrency(value: number | undefined | null, currency: string): string {
  if (value === undefined || value === null || Number.isNaN(value)) return "—"; // Guard undefined/NaN
  const locale = currency === "₹" ? "en-IN" : "en-US"; // Use lakh/crore grouping for INR, thousand/million for USD
  return `${currency}${Number(value).toLocaleString(locale, {
    minimumFractionDigits: 2, // Always display 2 decimal digits
    maximumFractionDigits: 2,
  })}`;
}

/** Converts Python trade_events into TradingView Lightweight Charts v5 marker objects. */
export function toLightweightMarkers(events: TradeEventItem[]) {
  return events.map((ev) => {
    const isBuy = ev.side === "BUY"; // Green upward arrow for BUY, rose downward arrow for SELL
    return {
      time: ev.time, // Date bar on X-axis
      position: (isBuy ? "belowBar" : "aboveBar") as "belowBar" | "aboveBar", // Place arrow clearly outside curve
      color: isBuy ? "#10B981" : "#F43F5E", // Emerald for BUY, Rose for SELL
      shape: (isBuy ? "arrowUp" : "arrowDown") as "arrowUp" | "arrowDown", // Directional arrow icon
      text: isBuy ? "BUY" : "SELL", // Concise marker caption to keep chart uncluttered
    };
  });
}
