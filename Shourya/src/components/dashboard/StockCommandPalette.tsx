// Shourya/src/components/dashboard/StockCommandPalette.tsx - Zero-glitch Ctrl+K ShadCN Search Palette.
// Member: Shourya (UI).

import React, { useEffect, useMemo, useRef, useState } from "react";
import { Globe, IndianRupee, Loader2, Search, TrendingUp } from "lucide-react";
import { Dialog, DialogContent } from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";

export interface StockOption {
  symbol: string;
  name: string;
  exchange: string;
  market: string;
}

interface StockCommandPaletteProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSelectStock: (stock: StockOption) => void;
}

/** Ranks and filters local cached stocks instantaneously (0ms) without network flicker. */
function filterLocalWatchlist(watchlist: StockOption[], query: string, limit = 14): StockOption[] {
  const q = query.trim().toUpperCase();
  if (!q) return watchlist.slice(0, limit);

  const exact: StockOption[] = [];
  const starts: StockOption[] = [];
  const contains: StockOption[] = [];

  for (const item of watchlist) {
    const sym = item.symbol.toUpperCase();
    const name = item.name.toUpperCase();
    if (sym === q) exact.push(item);
    else if (sym.startsWith(q)) starts.push(item);
    else if (sym.includes(q) || name.includes(q)) contains.push(item);
  }
  return [...exact, ...starts, ...contains].slice(0, limit);
}

export const StockCommandPalette: React.FC<StockCommandPaletteProps> = ({
  open,
  onOpenChange,
  onSelectStock,
}) => {
  const [query, setQuery] = useState("");
  const [watchlist, setWatchlist] = useState<StockOption[]>([]);
  const [onlineExtra, setOnlineExtra] = useState<StockOption[]>([]);
  const [isFetchingOnline, setIsFetchingOnline] = useState(false);
  const [activeIndex, setActiveIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement | null>(null);

  // Fetch Prakshat's 100+ offline watchlist once so keystrokes never wait on network I/O
  useEffect(() => {
    fetch("/api/watchlist")
      .then((r) => (r.ok ? r.json() : { results: [] }))
      .then((data) => {
        if (Array.isArray(data.results)) setWatchlist(data.results);
      })
      .catch(() => {});
  }, []);

  // Auto-focus search input cleanly whenever palette opens
  useEffect(() => {
    if (open) {
      setActiveIndex(0);
      setTimeout(() => inputRef.current?.focus(), 10);
    } else {
      setQuery("");
      setOnlineExtra([]);
      setIsFetchingOnline(false);
    }
  }, [open]);

  // Synchronous 0ms local matches on every keystroke
  const localMatches = useMemo(() => filterLocalWatchlist(watchlist, query, 14), [watchlist, query]);

  // Optional debounced online Yahoo Finance enrichment only when local hits < 4, with AbortController
  useEffect(() => {
    if (!open) return;
    const trimmed = query.trim();
    if (trimmed.length < 2 || localMatches.length >= 4) {
      setOnlineExtra([]);
      setIsFetchingOnline(false);
      return;
    }

    const controller = new AbortController();
    const timer = setTimeout(async () => {
      setIsFetchingOnline(true);
      try {
        const res = await fetch(`/api/search?q=${encodeURIComponent(trimmed)}&limit=10`, {
          signal: controller.signal,
        });
        if (res.ok) {
          const json = await res.json();
          const seen = new Set(localMatches.map((m) => m.symbol.toUpperCase()));
          const extras = (json.results || []).filter(
            (item: StockOption) => !seen.has(item.symbol.toUpperCase())
          );
          setOnlineExtra(extras);
        }
      } catch (err: any) {
        if (err?.name !== "AbortError") setOnlineExtra([]);
      } finally {
        if (!controller.signal.aborted) setIsFetchingOnline(false);
      }
    }, 280);

    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [query, open, localMatches]);

  const combinedResults = useMemo(
    () => [...localMatches, ...onlineExtra].slice(0, 14),
    [localMatches, onlineExtra]
  );

  // Reset highlighted index when result list changes
  useEffect(() => {
    setActiveIndex(0);
  }, [query]);

  const usStocks = combinedResults.filter((r) => !r.market.toLowerCase().includes("india"));
  const indiaStocks = combinedResults.filter((r) => r.market.toLowerCase().includes("india"));
  const orderedFlat = [...usStocks, ...indiaStocks];

  const handleChoose = (stock: StockOption) => {
    onSelectStock(stock);
    onOpenChange(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (orderedFlat.length === 0) return;
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setActiveIndex((prev) => (prev + 1) % orderedFlat.length);
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setActiveIndex((prev) => (prev - 1 + orderedFlat.length) % orderedFlat.length);
    } else if (e.key === "Enter") {
      e.preventDefault();
      const target = orderedFlat[activeIndex] || orderedFlat[0];
      if (target) handleChoose(target);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="gap-0">
        {/* Search Header Input (fixed height, inline spinner prevents layout shifting) */}
        <div className="flex items-center border-b border-border px-3 pr-10 h-12 shrink-0 bg-popover">
          <Search className="mr-2.5 h-4 w-4 shrink-0 text-muted-foreground" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Search US or Indian stocks (e.g. NVDA, Tata, ^NSEI)..."
            className="flex-1 bg-transparent text-sm text-foreground outline-none placeholder:text-muted-foreground"
          />
          {isFetchingOnline && <Loader2 className="h-3.5 w-3.5 animate-spin text-indigo-400 shrink-0 ml-2" />}
        </div>

        {/* Fixed-height Results Area (eliminates jumping/flickering while typing) */}
        <div className="h-[340px] overflow-y-auto p-2 space-y-2 bg-popover">
          {orderedFlat.length === 0 ? (
            <div className="flex h-full items-center justify-center text-xs text-muted-foreground px-4 text-center">
              {isFetchingOnline
                ? "Searching Yahoo Finance global markets..."
                : "No matching tickers found. Try SPY, AAPL, NVDA, or RELIANCE.NS."}
            </div>
          ) : (
            <>
              {usStocks.length > 0 && (
                <div>
                  <div className="px-2 py-1 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
                    US &amp; Global Equities / ETFs
                  </div>
                  <div className="space-y-0.5">
                    {usStocks.map((item) => {
                      const idx = orderedFlat.findIndex((x) => x.symbol === item.symbol);
                      const isActive = idx === activeIndex;
                      return (
                        <button
                          key={item.symbol}
                          type="button"
                          onMouseEnter={() => setActiveIndex(idx)}
                          onClick={() => handleChoose(item)}
                          className={`w-full flex items-center justify-between rounded-md px-2.5 py-2 text-left text-xs transition-colors ${
                            isActive ? "bg-accent text-accent-foreground" : "hover:bg-accent/60"
                          }`}
                        >
                          <div className="flex items-center gap-2.5 min-w-0">
                            <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-md border border-border bg-muted/60">
                              <Globe className="h-3.5 w-3.5 text-indigo-400" />
                            </div>
                            <div className="flex flex-col min-w-0">
                              <span className="font-mono font-semibold text-foreground">{item.symbol}</span>
                              <span className="truncate text-[11px] text-muted-foreground">{item.name}</span>
                            </div>
                          </div>
                          <div className="flex items-center gap-1.5 shrink-0 ml-2">
                            {item.exchange && <Badge variant="outline">{item.exchange}</Badge>}
                            <Badge variant="indigo">$ USD</Badge>
                          </div>
                        </button>
                      );
                    })}
                  </div>
                </div>
              )}

              {indiaStocks.length > 0 && (
                <div>
                  <div className="px-2 py-1 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
                    Indian Markets (NSE / BSE)
                  </div>
                  <div className="space-y-0.5">
                    {indiaStocks.map((item) => {
                      const idx = orderedFlat.findIndex((x) => x.symbol === item.symbol);
                      const isActive = idx === activeIndex;
                      return (
                        <button
                          key={item.symbol}
                          type="button"
                          onMouseEnter={() => setActiveIndex(idx)}
                          onClick={() => handleChoose(item)}
                          className={`w-full flex items-center justify-between rounded-md px-2.5 py-2 text-left text-xs transition-colors ${
                            isActive ? "bg-accent text-accent-foreground" : "hover:bg-accent/60"
                          }`}
                        >
                          <div className="flex items-center gap-2.5 min-w-0">
                            <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-md border border-border bg-muted/60">
                              <IndianRupee className="h-3.5 w-3.5 text-emerald-400" />
                            </div>
                            <div className="flex flex-col min-w-0">
                              <span className="font-mono font-semibold text-foreground">{item.symbol}</span>
                              <span className="truncate text-[11px] text-muted-foreground">{item.name}</span>
                            </div>
                          </div>
                          <div className="flex items-center gap-1.5 shrink-0 ml-2">
                            {item.exchange && <Badge variant="outline">{item.exchange}</Badge>}
                            <Badge variant="success">₹ INR</Badge>
                          </div>
                        </button>
                      );
                    })}
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        {/* Footer Hints */}
        <div className="flex items-center justify-between border-t border-border px-3 py-2 text-[11px] text-muted-foreground bg-muted/20 shrink-0">
          <span className="flex items-center gap-1.5">
            <TrendingUp className="h-3 w-3 text-indigo-400" />
            ↑↓ Navigate · ↵ Select · Instant local + Yahoo Finance
          </span>
          <span className="font-mono">ESC to close</span>
        </div>
      </DialogContent>
    </Dialog>
  );
};
