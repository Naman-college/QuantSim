// Shourya/src/App.tsx - Main ShadCN UI Workspace connecting TopNavbar, SidebarPanel, Tabs, Charts & FastAPI.
// Member: Shourya (UI) — communicates with Naman's FastAPI backend (/api/*) & Prakshat's React charts.

import React, { useCallback, useEffect, useState } from "react";
import { BarChart3, Layers } from "lucide-react";
import { Toaster, toast } from "sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { TopNavbar } from "@/components/dashboard/TopNavbar";
import { SidebarPanel, type StrategyConfigState } from "@/components/dashboard/SidebarPanel";
import { StockCommandPalette, type StockOption } from "@/components/dashboard/StockCommandPalette";
import { KpiGrid } from "@/components/dashboard/KpiGrid";
import { TradeLogPanel } from "@/components/dashboard/TradeLogPanel";
import { ComparisonDashboard } from "@/components/dashboard/ComparisonDashboard";
import { SingleStrategyChart } from "@prakshat/SingleStrategyChart";
import type { ComparisonResponse, SingleBacktestResponse } from "@prakshat/chartTransformers";

const DEFAULT_CONFIG: StrategyConfigState = {
  lumpAllocationPct: 100,
  lumpCashYieldPct: 4.0,
  lumpFeePct: 0.1,
  dipPct: 2.0,
  dipWindow: 1,
  dipHoldDays: 10,
  dipTakeProfitPct: 0.0,
  dipStopLossPct: 0.0,
  dipFeePct: 0.1,
  sipAmount: 500,
  sipFrequency: "Monthly",
  sipStepUpPct: 0.0,
  sipDipBoostPct: 0.0,
  sipFeePct: 0.0,
  targetGainPct: 5.0,
  stopLossPct: 3.0,
  trailingStop: false,
  trailingStopPct: 3.0,
  maxHoldDays: 0,
  cooldownDays: 1,
  tslFeePct: 0.1,
  maFast: 20,
  maSlow: 50,
  maType: "SMA",
  useTrendFilter: false,
  trendFilterPeriod: 200,
  maStopLossPct: 0.0,
  maFeePct: 0.1,
};

function getCurrencyForSymbol(symbol: string): string {
  const s = symbol.trim().toUpperCase();
  if (s.endsWith(".NS") || s.endsWith(".BO") || s.startsWith("^NSE") || s.startsWith("^BSE")) {
    return "₹";
  }
  return "$";
}

function buildStrategyParamsMap(cfg: StrategyConfigState): Record<string, Record<string, unknown>> {
  return {
    "1. Lump Sum Investment": {
      allocation_pct: cfg.lumpAllocationPct,
      cash_interest_rate_pct: cfg.lumpCashYieldPct,
      transaction_fee_pct: cfg.lumpFeePct,
    },
    "2. Buying Dips": {
      dip_pct: cfg.dipPct,
      dip_window: cfg.dipWindow,
      hold_days: cfg.dipHoldDays,
      take_profit_pct: cfg.dipTakeProfitPct,
      stop_loss_pct: cfg.dipStopLossPct,
      transaction_fee_pct: cfg.dipFeePct,
    },
    "3. SIP (Systematic Investment Plan)": {
      monthly_installment: cfg.sipAmount,
      frequency: cfg.sipFrequency,
      step_up_pct: cfg.sipStepUpPct,
      dip_boost_pct: cfg.sipDipBoostPct,
      transaction_fee_pct: cfg.sipFeePct,
    },
    "4. Target Gain & Stop Loss": {
      target_gain_pct: cfg.targetGainPct,
      stop_loss_pct: cfg.stopLossPct,
      trailing_stop: cfg.trailingStop,
      trailing_stop_pct: cfg.trailingStopPct,
      max_hold_days: cfg.maxHoldDays,
      re_entry_wait_days: cfg.cooldownDays,
      transaction_fee_pct: cfg.tslFeePct,
    },
    "5. Moving Average Crossover": {
      fast_period: cfg.maFast,
      slow_period: cfg.maSlow,
      ma_type: cfg.maType,
      use_trend_filter: cfg.useTrendFilter,
      trend_filter_period: cfg.trendFilterPeriod,
      stop_loss_pct: cfg.maStopLossPct,
      transaction_fee_pct: cfg.maFeePct,
    },
  };
}

export default function App() {
  const [isDark, setIsDark] = useState(true);
  const [searchOpen, setSearchOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<"single" | "compare">("single");

  const [selectedSymbol, setSelectedSymbol] = useState("SPY");
  const [selectedName, setSelectedName] = useState("SPDR S&P 500 ETF Trust");
  const [strategyName, setStrategyName] = useState("1. Lump Sum Investment");
  const [capital, setCapital] = useState(10000);
  const [startDate, setStartDate] = useState("2020-01-01");
  const [config, setConfig] = useState<StrategyConfigState>(DEFAULT_CONFIG);

  const [singleResult, setSingleResult] = useState<SingleBacktestResponse | null>(null);
  const [compareResult, setCompareResult] = useState<ComparisonResponse | null>(null);
  const [isRunningSingle, setIsRunningSingle] = useState(false);
  const [isRunningCompare, setIsRunningCompare] = useState(false);

  const currency = getCurrencyForSymbol(selectedSymbol);

  // Sync Tailwind '.dark' class on <html> root
  useEffect(() => {
    const root = document.documentElement;
    if (isDark) root.classList.add("dark");
    else root.classList.remove("dark");
  }, [isDark]);

  // Register Ctrl+K / Cmd+K global shortcut to open ShadCN Command Palette
  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setSearchOpen((prev) => !prev);
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, []);

  const runSingleBacktest = useCallback(
    async (tickerOverride?: string, stratOverride?: string) => {
      const targetTicker = tickerOverride ?? selectedSymbol;
      const targetStrat = stratOverride ?? strategyName;
      const allParams = buildStrategyParamsMap(config);

      if (targetStrat.startsWith("5.") && config.maFast >= config.maSlow) {
        toast.error("Fast MA period must be strictly less than Slow MA period.");
        return;
      }

      setIsRunningSingle(true);
      try {
        const res = await fetch("/api/backtest", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            ticker: targetTicker,
            strategy_name: targetStrat,
            start_date: startDate,
            initial_capital: capital,
            strategy_params: allParams[targetStrat] || {},
          }),
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Backtest failed");
        setSingleResult(data);
        setActiveTab("single");
      } catch (err: any) {
        toast.error(err.message || "Unable to complete backtest");
      } finally {
        setIsRunningSingle(false);
      }
    },
    [selectedSymbol, strategyName, startDate, capital, config]
  );

  const runComparison = useCallback(
    async (tickerOverride?: string) => {
      const targetTicker = tickerOverride ?? selectedSymbol;
      const allParams = buildStrategyParamsMap(config);

      setIsRunningCompare(true);
      setActiveTab("compare");
      try {
        const res = await fetch("/api/compare", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            ticker: targetTicker,
            start_date: startDate,
            initial_capital: capital,
            strategy_params_dict: allParams,
          }),
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Comparison failed");
        setCompareResult(data);
      } catch (err: any) {
        toast.error(err.message || "Unable to compare strategies");
      } finally {
        setIsRunningCompare(false);
      }
    },
    [selectedSymbol, startDate, capital, config]
  );

  // Run initial SPY backtest on startup
  useEffect(() => {
    runSingleBacktest("SPY", "1. Lump Sum Investment");
  }, []);

  const handleSelectStock = (stock: StockOption) => {
    setSelectedSymbol(stock.symbol);
    setSelectedName(stock.name);
    toast.success(`Switched asset to ${stock.symbol}`);
    if (activeTab === "compare") runComparison(stock.symbol);
    else runSingleBacktest(stock.symbol);
  };

  const handleQuickSelect = (symbol: string, label: string) => {
    setSelectedSymbol(symbol);
    setSelectedName(label);
    if (activeTab === "compare") runComparison(symbol);
    else runSingleBacktest(symbol);
  };

  const handleTabChange = (val: string) => {
    const next = val as "single" | "compare";
    setActiveTab(next);
    if (next === "compare") {
      runComparison();
    }
  };

  return (
    <TooltipProvider delayDuration={150}>
      <div className="min-h-screen flex flex-col bg-background text-foreground">
        <Toaster theme={isDark ? "dark" : "light"} richColors position="bottom-right" />

        <StockCommandPalette
          open={searchOpen}
          onOpenChange={setSearchOpen}
          onSelectStock={handleSelectStock}
        />

        <TopNavbar
          selectedSymbol={selectedSymbol}
          isDark={isDark}
          isRunning={isRunningSingle || isRunningCompare}
          onToggleTheme={() => setIsDark((d) => !d)}
          onOpenSearch={() => setSearchOpen(true)}
          onQuickSelect={handleQuickSelect}
          onRunBacktest={() => (activeTab === "compare" ? runComparison() : runSingleBacktest())}
        />

        <div className="flex flex-1 flex-col lg:flex-row min-h-0">
          <SidebarPanel
            selectedSymbol={selectedSymbol}
            selectedName={selectedName}
            currency={currency}
            strategyName={strategyName}
            capital={capital}
            startDate={startDate}
            config={config}
            isRunning={isRunningSingle || isRunningCompare}
            onOpenSearch={() => setSearchOpen(true)}
            onStrategyChange={setStrategyName}
            onCapitalChange={setCapital}
            onStartDateChange={setStartDate}
            onConfigChange={(patch) => setConfig((prev) => ({ ...prev, ...patch }))}
            onRunBacktest={() => runSingleBacktest()}
            onCompareAll={() => runComparison()}
          />

          {/* Main Analytical Workspace */}
          <main className="flex-1 p-4 flex flex-col min-w-0">
            <Tabs value={activeTab} onValueChange={handleTabChange} className="flex flex-col flex-1">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <TabsList>
                  <TabsTrigger value="single">
                    <BarChart3 className="h-3.5 w-3.5 text-indigo-400" />
                    Single Strategy Backtest
                  </TabsTrigger>
                  <TabsTrigger value="compare">
                    <Layers className="h-3.5 w-3.5 text-emerald-400" />
                    All Strategies Comparison
                  </TabsTrigger>
                </TabsList>

                {singleResult && activeTab === "single" && (
                  <div className="hidden md:flex items-center gap-2 text-xs text-muted-foreground font-mono">
                    <span>{singleResult.ticker}</span>
                    <span>·</span>
                    <span>{singleResult.strategy_name}</span>
                  </div>
                )}
              </div>

              <TabsContent value="single" className="flex-1 flex flex-col gap-4">
                <KpiGrid
                  metrics={singleResult?.metrics ?? null}
                  benchMetrics={singleResult?.benchmark_metrics ?? null}
                  currency={singleResult?.currency ?? currency}
                  initialCapital={singleResult?.initial_capital ?? capital}
                  isLoading={isRunningSingle}
                />

                <div className="grid grid-cols-1 xl:grid-cols-12 gap-4 flex-1 min-h-[440px]">
                  <div className="xl:col-span-8 min-h-[400px]">
                    <SingleStrategyChart
                      data={singleResult}
                      isDark={isDark}
                      isLoading={isRunningSingle}
                    />
                  </div>
                  <div className="xl:col-span-4 min-h-[400px]">
                    <TradeLogPanel
                      events={singleResult?.trade_events ?? []}
                      currency={singleResult?.currency ?? currency}
                    />
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="compare" className="flex-1">
                <ComparisonDashboard
                  data={compareResult}
                  isDark={isDark}
                  isLoading={isRunningCompare}
                />
              </TabsContent>
            </Tabs>
          </main>
        </div>
      </div>
    </TooltipProvider>
  );
}
