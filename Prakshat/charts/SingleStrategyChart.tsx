// Prakshat/charts/SingleStrategyChart.tsx - Interactive TradingView Lightweight Charts v5 React component.
// Member: Prakshat (Finance API and Charts API Integration).

import React, { useEffect, useRef, useState } from "react"; // React hooks for DOM refs, lifecycle, and chart view state
import {
  createChart,
  AreaSeries,
  LineSeries,
  CandlestickSeries,
  CrosshairMode,
  LineStyle,
  createSeriesMarkers,
  type IChartApi,
  type ISeriesApi,
  type ISeriesMarkersPluginApi,
  type Time,
} from "lightweight-charts"; // TradingView Lightweight Charts v5 modular ESM API
import { TrendingUp, CandlestickChart, ArrowDownRight, Eye, EyeOff } from "lucide-react"; // Clean vector icons
import { formatCurrency, toLightweightMarkers, type SingleBacktestResponse } from "./chartTransformers"; // Prakshat data formatters

interface SingleStrategyChartProps {
  data: SingleBacktestResponse | null; // Backtest payload from Naman's FastAPI endpoint
  isDark: boolean; // Active ShadCN theme mode ('dark' vs 'light')
  isLoading: boolean; // True while backend computes a new backtest
}

type ChartMode = "equity" | "candle" | "drawdown"; // Supported sub-views
type RangePreset = "1M" | "3M" | "6M" | "YTD" | "1Y" | "ALL"; // Google Finance zoom presets

const RANGE_PRESETS: RangePreset[] = ["1M", "3M", "6M", "YTD", "1Y", "ALL"]; // Toolbar button list

export const SingleStrategyChart: React.FC<SingleStrategyChartProps> = ({ data, isDark, isLoading }) => {
  const containerRef = useRef<HTMLDivElement | null>(null); // DOM mount point for Lightweight Charts canvas
  const chartRef = useRef<IChartApi | null>(null); // Holds active chart instance
  const equitySeriesRef = useRef<ISeriesApi<"Area"> | null>(null); // Strategy Equity AreaSeries
  const benchSeriesRef = useRef<ISeriesApi<"Line"> | null>(null); // Buy & Hold dashed LineSeries
  const candleSeriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null); // OHLC CandlestickSeries
  const maFastSeriesRef = useRef<ISeriesApi<"Line"> | null>(null); // Fast SMA/EMA overlay line
  const maSlowSeriesRef = useRef<ISeriesApi<"Line"> | null>(null); // Slow SMA/EMA overlay line
  const maTrendSeriesRef = useRef<ISeriesApi<"Line"> | null>(null); // 200-SMA macro trend filter line
  const drawdownSeriesRef = useRef<ISeriesApi<"Area"> | null>(null); // Underwater Drawdown % AreaSeries
  const markerPluginRef = useRef<ISeriesMarkersPluginApi<Time> | null>(null); // v5 Trade Marker plugin handle

  const [viewMode, setViewMode] = useState<ChartMode>("equity"); // Active chart tab
  const [activeRange, setActiveRange] = useState<RangePreset>("ALL"); // Highlighted range pill
  const [showMarkers, setShowMarkers] = useState<boolean>(true); // Toggle BUY/SELL arrow markers
  const [showBenchmark, setShowBenchmark] = useState<boolean>(true); // Toggle Buy & Hold baseline curve
  const [hud, setHud] = useState<{
    date: string;
    primary: string;
    deltaPct: number | null;
    benchText: string;
  }>({ date: "—", primary: "—", deltaPct: null, benchText: "" }); // Floating crosshair HUD state

  // Helper to update HUD readout to latest bar when mouse is not hovering over chart
  const resetHudToLatest = (payload: SingleBacktestResponse | null, mode: ChartMode) => {
    if (!payload) return;
    const { charts, currency } = payload;
    if (mode === "equity" && charts.equityData.length > 0) {
      const first = charts.equityData[0]; // Day 1 value
      const last = charts.equityData[charts.equityData.length - 1]; // Final value
      const pct = first.value > 0 ? ((last.value - first.value) / first.value) * 100 : 0; // Total return %
      let benchText = "";
      if (charts.benchmarkData.length > 0) {
        const bFirst = charts.benchmarkData[0];
        const bLast = charts.benchmarkData[charts.benchmarkData.length - 1];
        const bPct = bFirst.value > 0 ? ((bLast.value - bFirst.value) / bFirst.value) * 100 : 0;
        benchText = `Buy & Hold: ${formatCurrency(bLast.value, currency)} (${bPct >= 0 ? "+" : ""}${bPct.toFixed(1)}%)`;
      }
      setHud({ date: last.time, primary: formatCurrency(last.value, currency), deltaPct: pct, benchText });
    } else if (mode === "candle" && charts.candleData.length > 0) {
      const last = charts.candleData[charts.candleData.length - 1];
      setHud({
        date: last.time,
        primary: `O ${formatCurrency(last.open, currency)} · H ${formatCurrency(last.high, currency)} · L ${formatCurrency(last.low, currency)} · C ${formatCurrency(last.close, currency)}`,
        deltaPct: null,
        benchText: charts.indicators.maFast.length > 0 ? "Overlay: Fast MA (Indigo) / Slow MA (Amber)" : "Daily OHLC Price Action",
      });
    } else if (mode === "drawdown" && charts.drawdownData.length > 0) {
      const last = charts.drawdownData[charts.drawdownData.length - 1];
      setHud({
        date: last.time,
        primary: `${last.value.toFixed(2)}%`,
        deltaPct: null,
        benchText: "Peak-to-Trough Underwater Equity Decline",
      });
    }
  };

  // Initialize TradingView Lightweight Chart instance once on mount
  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;

    const chart = createChart(el, {
      width: el.clientWidth,
      height: el.clientHeight,
      layout: {
        background: { color: "transparent" }, // Let ShadCN Card background shine through
        textColor: isDark ? "#A1A1AA" : "#71717A", // Zinc-400 / Zinc-500 axis text
        fontFamily: "Inter, -apple-system, sans-serif",
        fontSize: 11,
      },
      grid: {
        vertLines: { color: isDark ? "rgba(39, 39, 42, 0.55)" : "rgba(228, 228, 231, 0.7)" }, // Crisp subtle grid
        horzLines: { color: isDark ? "rgba(39, 39, 42, 0.55)" : "rgba(228, 228, 231, 0.7)" },
      },
      crosshair: { mode: CrosshairMode.Normal },
      rightPriceScale: {
        borderColor: isDark ? "#27272A" : "#E4E4E7",
        autoScale: true,
        scaleMargins: { top: 0.14, bottom: 0.1 },
      },
      timeScale: {
        borderColor: isDark ? "#27272A" : "#E4E4E7",
        timeVisible: true,
        rightOffset: 0,
        fixLeftEdge: true,
        fixRightEdge: true,
      },
    });

    // Create all series layers (visibility toggled dynamically per active tab)
    const eq = chart.addSeries(AreaSeries, {
      lineColor: "#6366F1", // Indigo-500 primary strategy stroke
      topColor: "rgba(99, 102, 241, 0.34)",
      bottomColor: "rgba(99, 102, 241, 0.01)",
      lineWidth: 2,
    });

    const bench = chart.addSeries(LineSeries, {
      color: "#71717A", // Zinc-500 dashed Buy & Hold benchmark
      lineWidth: 1,
      lineStyle: LineStyle.Dashed,
    });

    const candle = chart.addSeries(CandlestickSeries, {
      upColor: "#10B981",
      downColor: "#F43F5E",
      borderUpColor: "#10B981",
      borderDownColor: "#F43F5E",
      wickUpColor: "#10B981",
      wickDownColor: "#F43F5E",
      visible: false,
    });

    const maFast = chart.addSeries(LineSeries, { color: "#6366F1", lineWidth: 2, visible: false }); // Fast MA
    const maSlow = chart.addSeries(LineSeries, { color: "#F59E0B", lineWidth: 2, visible: false }); // Slow MA
    const maTrend = chart.addSeries(LineSeries, {
      color: "#EC4899",
      lineWidth: 1,
      lineStyle: LineStyle.Dotted,
      visible: false,
    }); // 200-SMA filter

    const dd = chart.addSeries(AreaSeries, {
      lineColor: "#F43F5E",
      topColor: "rgba(244, 63, 94, 0.02)",
      bottomColor: "rgba(244, 63, 94, 0.32)",
      lineWidth: 2,
      visible: false,
      priceFormat: { type: "custom", formatter: (p: number) => `${Number(p).toFixed(2)}%` },
    });

    chartRef.current = chart;
    equitySeriesRef.current = eq;
    benchSeriesRef.current = bench;
    candleSeriesRef.current = candle;
    maFastSeriesRef.current = maFast;
    maSlowSeriesRef.current = maSlow;
    maTrendSeriesRef.current = maTrend;
    drawdownSeriesRef.current = dd;

    // ResizeObserver automatically keeps chart sized cleanly inside responsive flexbox/splitters
    const ro = new ResizeObserver((entries) => {
      for (const entry of entries) {
        const { width, height } = entry.contentRect;
        if (width > 0 && height > 0) chart.applyOptions({ width, height });
      }
    });
    ro.observe(el);

    return () => {
      ro.disconnect(); // Clean up observer on unmount
      chart.remove(); // Destroy Lightweight Charts canvas cleanly
      chartRef.current = null;
    };
  }, []);

  // Re-apply Light/Dark ShadCN theme palette without destroying series data
  useEffect(() => {
    if (!chartRef.current) return;
    chartRef.current.applyOptions({
      layout: { textColor: isDark ? "#A1A1AA" : "#71717A" },
      grid: {
        vertLines: { color: isDark ? "rgba(39, 39, 42, 0.55)" : "rgba(228, 228, 231, 0.7)" },
        horzLines: { color: isDark ? "rgba(39, 39, 42, 0.55)" : "rgba(228, 228, 231, 0.7)" },
      },
      rightPriceScale: { borderColor: isDark ? "#27272A" : "#E4E4E7" },
      timeScale: { borderColor: isDark ? "#27272A" : "#E4E4E7" },
    });
  }, [isDark]);

  // Push new backtest dataset into TradingView series & attach crosshair subscription
  useEffect(() => {
    const chart = chartRef.current;
    if (!chart || !data) return;

    const { charts, currency, trade_events } = data;
    const priceFmt = { type: "custom" as const, formatter: (p: number) => formatCurrency(p, currency) };

    equitySeriesRef.current?.applyOptions({ priceFormat: priceFmt });
    benchSeriesRef.current?.applyOptions({ priceFormat: priceFmt });
    candleSeriesRef.current?.applyOptions({ priceFormat: priceFmt });

    equitySeriesRef.current?.setData(charts.equityData as any);
    benchSeriesRef.current?.setData(charts.benchmarkData as any);
    candleSeriesRef.current?.setData(charts.candleData as any);
    maFastSeriesRef.current?.setData(charts.indicators.maFast as any);
    maSlowSeriesRef.current?.setData(charts.indicators.maSlow as any);
    maTrendSeriesRef.current?.setData(charts.indicators.maTrend as any);
    drawdownSeriesRef.current?.setData(charts.drawdownData as any);

    // Refresh BUY/SELL markers on Equity Curve
    if (markerPluginRef.current) {
      try { markerPluginRef.current.detach(); } catch {}
      markerPluginRef.current = null;
    }
    if (showMarkers && equitySeriesRef.current && trade_events.length > 0) {
      markerPluginRef.current = createSeriesMarkers(
        equitySeriesRef.current,
        toLightweightMarkers(trade_events) as any
      );
    }

    chart.timeScale().fitContent();
    setActiveRange("ALL");
    resetHudToLatest(data, viewMode);

    // Subscribe live crosshair hover updates for floating HUD
    const handler = (param: any) => {
      if (!param || !param.time || !param.seriesData) {
        resetHudToLatest(data, viewMode);
        return;
      }
      const timeStr =
        typeof param.time === "string"
          ? param.time
          : `${param.time.year}-${String(param.time.month).padStart(2, "0")}-${String(param.time.day).padStart(2, "0")}`;

      if (viewMode === "equity") {
        const eqPt = equitySeriesRef.current ? param.seriesData.get(equitySeriesRef.current) : null;
        const bnPt = benchSeriesRef.current ? param.seriesData.get(benchSeriesRef.current) : null;
        if (eqPt && charts.equityData.length > 0) {
          const startVal = charts.equityData[0].value;
          const pct = startVal > 0 ? ((eqPt.value - startVal) / startVal) * 100 : 0;
          let benchText = "";
          if (bnPt && charts.benchmarkData.length > 0) {
            const bStart = charts.benchmarkData[0].value;
            const bPct = bStart > 0 ? ((bnPt.value - bStart) / bStart) * 100 : 0;
            benchText = `Buy & Hold: ${formatCurrency(bnPt.value, currency)} (${bPct >= 0 ? "+" : ""}${bPct.toFixed(1)}%)`;
          }
          setHud({ date: timeStr, primary: formatCurrency(eqPt.value, currency), deltaPct: pct, benchText });
        }
      } else if (viewMode === "candle") {
        const cPt = candleSeriesRef.current ? param.seriesData.get(candleSeriesRef.current) : null;
        if (cPt) {
          setHud({
            date: timeStr,
            primary: `O ${formatCurrency(cPt.open, currency)} · H ${formatCurrency(cPt.high, currency)} · L ${formatCurrency(cPt.low, currency)} · C ${formatCurrency(cPt.close, currency)}`,
            deltaPct: null,
            benchText: charts.indicators.maFast.length > 0 ? "Overlay: Fast MA (Indigo) / Slow MA (Amber)" : "Daily OHLC Candlestick",
          });
        }
      } else if (viewMode === "drawdown") {
        const ddPt = drawdownSeriesRef.current ? param.seriesData.get(drawdownSeriesRef.current) : null;
        if (ddPt) {
          setHud({
            date: timeStr,
            primary: `${Number(ddPt.value).toFixed(2)}%`,
            deltaPct: null,
            benchText: "Peak-to-Trough Underwater Drawdown",
          });
        }
      }
    };

    chart.subscribeCrosshairMove(handler);
    return () => {
      chart.unsubscribeCrosshairMove(handler);
    };
  }, [data, viewMode, showMarkers]);

  // Toggle series visibility cleanly whenever user switches between Equity, Candles, or Drawdown
  useEffect(() => {
    equitySeriesRef.current?.applyOptions({ visible: viewMode === "equity" });
    benchSeriesRef.current?.applyOptions({ visible: viewMode === "equity" && showBenchmark });
    candleSeriesRef.current?.applyOptions({ visible: viewMode === "candle" });
    maFastSeriesRef.current?.applyOptions({ visible: viewMode === "candle" && (data?.charts.indicators.maFast.length ?? 0) > 0 });
    maSlowSeriesRef.current?.applyOptions({ visible: viewMode === "candle" && (data?.charts.indicators.maSlow.length ?? 0) > 0 });
    maTrendSeriesRef.current?.applyOptions({ visible: viewMode === "candle" && (data?.charts.indicators.maTrend.length ?? 0) > 0 });
    drawdownSeriesRef.current?.applyOptions({ visible: viewMode === "drawdown" });
    resetHudToLatest(data, viewMode);
  }, [viewMode, showBenchmark, data]);

  // Apply 1M / 3M / 6M / YTD / 1Y / ALL range zoom on X-axis
  const handleRangeSelect = (preset: RangePreset) => {
    setActiveRange(preset);
    const chart = chartRef.current;
    const pts = data?.charts.equityData;
    if (!chart || !pts || pts.length === 0) return;

    if (preset === "ALL") {
      chart.timeScale().fitContent();
      return;
    }

    const latest = new Date(pts[pts.length - 1].time);
    let target = new Date(latest);
    if (preset === "1M") target.setMonth(target.getMonth() - 1);
    else if (preset === "3M") target.setMonth(target.getMonth() - 3);
    else if (preset === "6M") target.setMonth(target.getMonth() - 6);
    else if (preset === "YTD") target = new Date(latest.getFullYear(), 0, 1);
    else if (preset === "1Y") target.setFullYear(target.getFullYear() - 1);

    let startIdx = 0;
    for (let i = 0; i < pts.length; i++) {
      if (new Date(pts[i].time) >= target) {
        startIdx = i;
        break;
      }
    }
    chart.timeScale().setVisibleLogicalRange({ from: startIdx, to: pts.length - 1 });
  };

  return (
    <div className="flex flex-col h-full w-full rounded-xl border border-border bg-card shadow-sm overflow-hidden">
      {/* Top Toolbar: View Mode Tabs + Toggles + Time Range Pills */}
      <div className="flex flex-wrap items-center justify-between gap-2 px-3 py-2.5 border-b border-border bg-card/80">
        {/* Segmented View Switcher */}
        <div className="inline-flex items-center rounded-lg bg-muted p-1 border border-border/60">
          <button
            type="button"
            onClick={() => setViewMode("equity")}
            className={`inline-flex items-center gap-1.5 rounded-md px-2.5 py-1 text-xs font-medium transition-all ${
              viewMode === "equity"
                ? "bg-background text-foreground shadow-sm"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            <TrendingUp className="h-3.5 w-3.5 text-indigo-500" />
            Equity Curve
          </button>
          <button
            type="button"
            onClick={() => setViewMode("candle")}
            className={`inline-flex items-center gap-1.5 rounded-md px-2.5 py-1 text-xs font-medium transition-all ${
              viewMode === "candle"
                ? "bg-background text-foreground shadow-sm"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            <CandlestickChart className="h-3.5 w-3.5 text-emerald-500" />
            Price &amp; MAs
          </button>
          <button
            type="button"
            onClick={() => setViewMode("drawdown")}
            className={`inline-flex items-center gap-1.5 rounded-md px-2.5 py-1 text-xs font-medium transition-all ${
              viewMode === "drawdown"
                ? "bg-background text-foreground shadow-sm"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            <ArrowDownRight className="h-3.5 w-3.5 text-rose-500" />
            Drawdown
          </button>
        </div>

        {/* Right Controls: Marker/Benchmark Toggles + Zoom Range Buttons */}
        <div className="flex items-center gap-2">
          {viewMode === "equity" && (
            <div className="hidden sm:flex items-center gap-1">
              <button
                type="button"
                onClick={() => setShowBenchmark((v) => !v)}
                className={`inline-flex items-center gap-1 rounded-md border px-2 py-1 text-[11px] font-medium transition-colors ${
                  showBenchmark
                    ? "border-border bg-secondary text-foreground"
                    : "border-transparent text-muted-foreground hover:bg-muted"
                }`}
                title="Toggle Buy & Hold benchmark line"
              >
                {showBenchmark ? <Eye className="h-3 w-3" /> : <EyeOff className="h-3 w-3" />}
                Benchmark
              </button>
              <button
                type="button"
                onClick={() => setShowMarkers((v) => !v)}
                className={`inline-flex items-center gap-1 rounded-md border px-2 py-1 text-[11px] font-medium transition-colors ${
                  showMarkers
                    ? "border-border bg-secondary text-foreground"
                    : "border-transparent text-muted-foreground hover:bg-muted"
                }`}
                title="Toggle BUY / SELL trade arrows"
              >
                {showMarkers ? <Eye className="h-3 w-3" /> : <EyeOff className="h-3 w-3" />}
                Trades
              </button>
            </div>
          )}

          <div className="inline-flex items-center rounded-lg bg-muted p-0.5 border border-border/60">
            {RANGE_PRESETS.map((preset) => (
              <button
                key={preset}
                type="button"
                onClick={() => handleRangeSelect(preset)}
                className={`rounded-md px-2 py-1 text-[11px] font-semibold transition-all ${
                  activeRange === preset
                    ? "bg-background text-foreground shadow-sm"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                {preset}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Chart Canvas Area + Floating HUD + Loading Blur */}
      <div className="relative flex-1 min-h-[340px] w-full">
        {/* Floating Glassmorphic Crosshair HUD */}
        <div className="pointer-events-none absolute top-3 left-3 z-10 flex flex-col gap-0.5 rounded-lg border border-border/70 bg-card/85 px-3 py-2 backdrop-blur-md shadow-sm">
          <span className="text-[11px] font-medium text-muted-foreground font-mono">{hud.date}</span>
          <div className="flex items-baseline gap-2">
            <span className="text-base sm:text-lg font-bold tracking-tight text-foreground font-mono">
              {hud.primary}
            </span>
            {hud.deltaPct !== null && (
              <span
                className={`inline-flex items-center rounded px-1.5 py-0.5 text-[11px] font-semibold font-mono ${
                  hud.deltaPct >= 0
                    ? "bg-emerald-500/15 text-emerald-500 border border-emerald-500/30"
                    : "bg-rose-500/15 text-rose-500 border border-rose-500/30"
                }`}
              >
                {hud.deltaPct >= 0 ? "+" : ""}
                {hud.deltaPct.toFixed(2)}%
              </span>
            )}
          </div>
          {hud.benchText && (
            <span className="text-[11px] text-muted-foreground font-mono">{hud.benchText}</span>
          )}
        </div>

        {/* Loading Shimmer Overlay */}
        {isLoading && (
          <div className="absolute inset-0 z-20 flex flex-col items-center justify-center gap-3 bg-background/75 backdrop-blur-sm">
            <div className="h-8 w-8 animate-spin rounded-full border-2 border-indigo-500/30 border-t-indigo-500" />
            <span className="text-xs font-medium tracking-wider uppercase text-muted-foreground">
              Running Quantitative Simulation...
            </span>
          </div>
        )}

        <div ref={containerRef} className="h-full w-full" />
      </div>
    </div>
  );
};
