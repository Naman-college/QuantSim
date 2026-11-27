// Shourya/src/components/dashboard/TopNavbar.tsx - Top ShadCN navigation bar with Ctrl+K trigger, quick tickers & theme switch.
// Member: Shourya (UI).

import React from "react";
import { Activity, Moon, Play, Search, Sun, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

const QUICK_TICKERS = [
  { symbol: "SPY", label: "SPY" },
  { symbol: "NVDA", label: "NVDA" },
  { symbol: "AAPL", label: "AAPL" },
  { symbol: "^NSEI", label: "NIFTY 50" },
  { symbol: "RELIANCE.NS", label: "RELIANCE" },
];

interface TopNavbarProps {
  selectedSymbol: string; // Currently active stock ticker
  isDark: boolean; // Dark vs Light theme state
  isRunning: boolean; // Loading spinner state
  onToggleTheme: () => void; // Theme toggle handler
  onOpenSearch: () => void; // Opens Ctrl+K Command Palette
  onQuickSelect: (symbol: string, name: string) => void; // 1-click quick asset switch
  onRunBacktest: () => void; // Runs active simulation
}

export const TopNavbar: React.FC<TopNavbarProps> = ({
  selectedSymbol,
  isDark,
  isRunning,
  onToggleTheme,
  onOpenSearch,
  onQuickSelect,
  onRunBacktest,
}) => {
  return (
    <header className="sticky top-0 z-30 flex h-14 items-center justify-between gap-3 border-b border-border bg-card/85 px-4 backdrop-blur-md">
      {/* Left: Brand Identity */}
      <div className="flex items-center gap-2.5 shrink-0">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600 text-white shadow-sm">
          <Activity className="h-4 w-4" />
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sm font-bold tracking-tight text-foreground">QuantSim</span>
          <Badge variant="indigo" className="hidden sm:inline-flex font-mono text-[10px]">
            v2.0
          </Badge>
        </div>
      </div>

      {/* Center: Command Search Trigger + Quick Ticker Pills */}
      <div className="flex items-center gap-2 flex-1 max-w-2xl justify-center">
        <button
          type="button"
          onClick={onOpenSearch}
          className="flex h-9 w-full max-w-xs items-center justify-between rounded-lg border border-input bg-background/80 px-3 text-xs text-muted-foreground shadow-sm transition-colors hover:bg-accent hover:text-foreground"
        >
          <span className="flex items-center gap-2 truncate">
            <Search className="h-3.5 w-3.5 shrink-0" />
            <span className="truncate">Search ticker or company...</span>
          </span>
          <kbd className="pointer-events-none hidden sm:inline-flex h-5 select-none items-center gap-1 rounded border border-border bg-muted px-1.5 font-mono text-[10px] font-medium text-muted-foreground">
            Ctrl K
          </kbd>
        </button>

        <div className="hidden lg:flex items-center gap-1">
          {QUICK_TICKERS.map((qt) => {
            const active = selectedSymbol.toUpperCase() === qt.symbol.toUpperCase();
            return (
              <button
                key={qt.symbol}
                type="button"
                onClick={() => onQuickSelect(qt.symbol, qt.label)}
                className={`rounded-md px-2 py-1 text-[11px] font-mono font-medium transition-all border ${
                  active
                    ? "border-primary/40 bg-primary/15 text-primary"
                    : "border-transparent text-muted-foreground hover:bg-muted hover:text-foreground"
                }`}
              >
                {qt.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Right: Theme Switcher + Run Backtest CTA */}
      <div className="flex items-center gap-2 shrink-0">
        <Button
          variant="outline"
          size="icon"
          onClick={onToggleTheme}
          title={isDark ? "Switch to Light Mode" : "Switch to Dark Mode"}
          className="h-8 w-8"
        >
          {isDark ? <Sun className="h-4 w-4 text-amber-400" /> : <Moon className="h-4 w-4 text-indigo-600" />}
        </Button>

        <Button size="sm" onClick={onRunBacktest} disabled={isRunning} className="h-8 font-semibold shadow-sm">
          {isRunning ? (
            <>
              <Loader2 className="h-3.5 w-3.5 animate-spin" />
              Simulating...
            </>
          ) : (
            <>
              <Play className="h-3.5 w-3.5 fill-current" />
              Run Backtest
            </>
          )}
        </Button>
      </div>
    </header>
  );
};
