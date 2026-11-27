// Prakshat/charts/ComparisonChart.tsx - Multi-Strategy Overlay Chart powered by TradingView Lightweight Charts v5.
// Member: Prakshat (Finance API and Charts API Integration).

import React, { useEffect, useRef, useState } from "react"; // React hooks for chart lifecycle and legend state
import {
  createChart,
  LineSeries,
  CrosshairMode,
  LineStyle,
  type IChartApi,
  type ISeriesApi,
} from "lightweight-charts"; // TradingView Lightweight Charts v5 ESM API
import { Layers } from "lucide-react"; // Overlay icon
import { formatCurrency, type ComparisonResponse } from "./chartTransformers"; // Currency & response types

interface ComparisonChartProps {
  data: ComparisonResponse | null; // All-5 strategy comparison payload from FastAPI
  isDark: boolean; // Active ShadCN theme
  isLoading: boolean; // True while all 5 strategies are running
}

type RangePreset = "1M" | "3M" | "6M" | "YTD" | "1Y" | "ALL"; // Zoom presets
const RANGE_PRESETS: RangePreset[] = ["1M", "3M", "6M", "YTD", "1Y", "ALL"]; // Button list

interface LegendEntry {
  name: string; // Strategy name
  color: string; // Hex color dot
  value: string; // Formatted equity readout
}

export const ComparisonChart: React.FC<ComparisonChartProps> = ({ data, isDark, isLoading }) => {
  const containerRef = useRef<HTMLDivElement | null>(null); // Chart DOM mount container
  const chartRef = useRef<IChartApi | null>(null); // LightweightCharts instance
  const seriesMapRef = useRef<Record<string, ISeriesApi<"Line">>>({}); // Maps strategy name -> LineSeries

  const [activeRange, setActiveRange] = useState<RangePreset>("ALL"); // Active zoom pill
  const [legendDate, setLegendDate] = useState<string>("—"); // Hovered/latest date shown in legend
  const [legendRows, setLegendRows] = useState<LegendEntry[]>([]); // Dynamic 5-strategy legend entries

  // Populate legend with final-day balances when crosshair leaves chart
  const resetLegendToLatest = (payload: ComparisonResponse | null) => {
    if (!payload || payload.lines.length === 0) return;
    const first = payload.lines[0];
    if (first.data.length > 0) {
      setLegendDate(`Latest · ${first.data[first.data.length - 1].time}`);
    }
    setLegendRows(
      payload.lines.map((line) => {
        const lastPt = line.data[line.data.length - 1];
        return {
          name: line.name,
          color: line.color,
          value: formatCurrency(lastPt?.value, payload.currency),
        };
      })
    );
  };

  // Initialize chart once on mount
  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;

    const chart = createChart(el, {
      width: el.clientWidth,
      height: el.clientHeight,
      layout: {
        background: { color: "transparent" },
        textColor: isDark ? "#A1A1AA" : "#71717A",
        fontFamily: "Inter, -apple-system, sans-serif",
        fontSize: 11,
      },
      grid: {
        vertLines: { color: isDark ? "rgba(39, 39, 42, 0.55)" : "rgba(228, 228, 231, 0.7)" },
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

    chartRef.current = chart;

    const ro = new ResizeObserver((entries) => {
      for (const entry of entries) {
        const { width, height } = entry.contentRect;
        if (width > 0 && height > 0) chart.applyOptions({ width, height });
      }
    });
    ro.observe(el);

    return () => {
      ro.disconnect();
      chart.remove();
      chartRef.current = null;
    };
  }, []);

  // Sync chart theme colors when user toggles Light/Dark mode
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

  // Render all 5 strategy LineSeries whenever comparison data updates
  useEffect(() => {
    const chart = chartRef.current;
    if (!chart || !data) return;

    // Remove previous series safely before adding new ticker curves
    Object.values(seriesMapRef.current).forEach((s) => {
      try { chart.removeSeries(s); } catch {}
    });
    seriesMapRef.current = {};

    data.lines.forEach((line) => {
      const s = chart.addSeries(LineSeries, {
        color: line.color,
        lineWidth: line.isBenchmark ? 1 : 2, // Thicker solid lines for active strategies
        lineStyle: line.isBenchmark ? LineStyle.Dashed : LineStyle.Solid,
        priceFormat: {
          type: "custom",
          formatter: (p: number) => formatCurrency(p, data.currency),
        },
      });
      s.setData(line.data as any);
      seriesMapRef.current[line.name] = s;
    });

    chart.timeScale().fitContent();
    setActiveRange("ALL");
    resetLegendToLatest(data);

    const handler = (param: any) => {
      if (!param || !param.time || !param.seriesData) {
        resetLegendToLatest(data);
        return;
      }
      const timeStr =
        typeof param.time === "string"
          ? param.time
          : `${param.time.year}-${String(param.time.month).padStart(2, "0")}-${String(param.time.day).padStart(2, "0")}`;
      setLegendDate(timeStr);

      setLegendRows(
        data.lines.map((line) => {
          const s = seriesMapRef.current[line.name];
          const pt = s ? param.seriesData.get(s) : null;
          return {
            name: line.name,
            color: line.color,
            value: formatCurrency(pt?.value, data.currency),
          };
        })
      );
    };

    chart.subscribeCrosshairMove(handler);
    return () => {
      chart.unsubscribeCrosshairMove(handler);
    };
  }, [data]);

  const handleRangeSelect = (preset: RangePreset) => {
    setActiveRange(preset);
    const chart = chartRef.current;
    const pts = data?.lines[0]?.data;
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
      {/* Toolbar */}
      <div className="flex items-center justify-between gap-2 px-3 py-2.5 border-b border-border bg-card/80">
        <div className="flex items-center gap-2">
          <Layers className="h-4 w-4 text-indigo-500" />
          <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            {data ? `${data.ticker} · All 5 Strategies Overlay` : "Comparative Equity Curves"}
          </span>
        </div>

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

      {/* Multi-line Canvas + Floating ShadCN Glass Legend */}
      <div className="relative flex-1 min-h-[340px] w-full">
        <div className="pointer-events-none absolute top-3 left-3 z-10 flex flex-col gap-1.5 rounded-lg border border-border/70 bg-card/85 px-3 py-2.5 backdrop-blur-md shadow-sm">
          <span className="text-[11px] font-semibold text-muted-foreground font-mono">{legendDate}</span>
          <div className="flex flex-col gap-1">
            {legendRows.map((row) => (
              <div key={row.name} className="flex items-center justify-between gap-4 text-[11px] font-mono">
                <span className="flex items-center gap-1.5 text-muted-foreground">
                  <span className="h-2 w-2 rounded-full shrink-0" style={{ backgroundColor: row.color }} />
                  <span className="truncate max-w-[175px]">{row.name}</span>
                </span>
                <span className="font-bold text-foreground">{row.value}</span>
              </div>
            ))}
          </div>
        </div>

        {isLoading && (
          <div className="absolute inset-0 z-20 flex flex-col items-center justify-center gap-3 bg-background/75 backdrop-blur-sm">
            <div className="h-8 w-8 animate-spin rounded-full border-2 border-indigo-500/30 border-t-indigo-500" />
            <span className="text-xs font-medium tracking-wider uppercase text-muted-foreground">
              Benchmarking All 5 Strategies...
            </span>
          </div>
        )}

        <div ref={containerRef} className="h-full w-full" />
      </div>
    </div>
  );
};
