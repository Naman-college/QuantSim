// Shourya/src/components/dashboard/StockCommandPalette.tsx - Ctrl+K ShadCN Command Palette for instant US & Indian stock search.
// Member: Shourya (UI).

import React, { useEffect, useState } from "react"; // React hooks for search query, debounce, and API results
import { Globe, IndianRupee, TrendingUp } from "lucide-react"; // Crisp market icons
import {
  CommandDialog,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command"; // ShadCN Command Palette primitives
import { Badge } from "@/components/ui/badge"; // ShadCN Badge for exchange & market tags

export interface StockOption {
  symbol: string; // Ticker symbol (e.g. 'SPY', 'RELIANCE.NS')
  name: string; // Company or ETF name
  exchange: string; // Exchange code (e.g. 'NASDAQ', 'NSE')
  market: string; // Region ('US' or 'India')
}

interface StockCommandPaletteProps {
  open: boolean; // Dialog open state
  onOpenChange: (open: boolean) => void; // Dialog close/open handler
  onSelectStock: (stock: StockOption) => void; // Callback when user clicks or presses Enter on a stock
}

export const StockCommandPalette: React.FC<StockCommandPaletteProps> = ({
  open,
  onOpenChange,
  onSelectStock,
}) => {
  const [query, setQuery] = useState(""); // Controlled search input
  const [results, setResults] = useState<StockOption[]>([]); // Matched tickers from /api/search
  const [loading, setLoading] = useState(false); // Loading indicator while querying Yahoo Finance

  // Debounced fetch from Naman's /api/search endpoint (backed by Prakshat's stock_search.py)
  useEffect(() => {
    if (!open) return; // Only search when dialog is open
    const timer = setTimeout(async () => {
      setLoading(true);
      try {
        const res = await fetch(`/api/search?q=${encodeURIComponent(query)}&limit=14`);
        if (res.ok) {
          const json = await res.json();
          setResults(json.results || []);
        }
      } catch {
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, 160); // 160ms debounce prevents excessive API hits while typing

    return () => clearTimeout(timer);
  }, [query, open]);

  // Split returned matches cleanly into US/Global vs Indian market sections
  const usStocks = results.filter((r) => !r.market.toLowerCase().includes("india"));
  const indiaStocks = results.filter((r) => r.market.toLowerCase().includes("india"));

  const handleChoose = (stock: StockOption) => {
    onSelectStock(stock); // Notify App.tsx
    onOpenChange(false); // Close palette
    setQuery(""); // Reset search text for next open
  };

  return (
    <CommandDialog open={open} onOpenChange={onOpenChange}>
      <CommandInput
        placeholder="Search US or Indian stocks, ETFs, or indices (e.g. NVDA, Tata, ^NSEI)..."
        value={query}
        onValueChange={setQuery}
      />
      <CommandList>
        {loading && (
          <div className="py-4 text-center text-xs text-muted-foreground">Searching global &amp; NSE markets...</div>
        )}
        {!loading && results.length === 0 && (
          <div className="py-6 text-center text-xs text-muted-foreground">
            No matching tickers found. Try symbols like SPY, AAPL, or RELIANCE.NS.
          </div>
        )}

        {usStocks.length > 0 && (
          <CommandGroup heading="US & Global Equities / ETFs">
            {usStocks.map((item) => (
              <CommandItem key={item.symbol} value={item.symbol} onSelect={() => handleChoose(item)}>
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
              </CommandItem>
            ))}
          </CommandGroup>
        )}

        {indiaStocks.length > 0 && (
          <CommandGroup heading="Indian Markets (NSE / BSE)">
            {indiaStocks.map((item) => (
              <CommandItem key={item.symbol} value={item.symbol} onSelect={() => handleChoose(item)}>
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
              </CommandItem>
            ))}
          </CommandGroup>
        )}

        <div className="flex items-center justify-between border-t border-border px-3 py-2 text-[11px] text-muted-foreground">
          <span className="flex items-center gap-1">
            <TrendingUp className="h-3 w-3 text-indigo-400" />
            100+ offline cached tickers + live Yahoo Finance API
          </span>
          <span className="font-mono">ESC to close</span>
        </div>
      </CommandList>
    </CommandDialog>
  );
};
