// Shourya/src/components/dashboard/TradeLogPanel.tsx - ShadCN Trade Execution History table with BUY/SELL filter pills.
// Member: Shourya (UI).

import React, { useState } from "react";
import { ArrowDownLeft, ArrowUpRight, History } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { formatCurrency, type TradeEventItem } from "@prakshat/chartTransformers";

interface TradeLogPanelProps {
  events: TradeEventItem[]; // Chronological trade events from backend
  currency: string; // '$' or '₹'
}

export const TradeLogPanel: React.FC<TradeLogPanelProps> = ({ events, currency }) => {
  const [filter, setFilter] = useState<"ALL" | "BUY" | "SELL">("ALL");

  // Show most recent trades at the top, optionally filtered by BUY / SELL side
  const displayed = [...events]
    .reverse()
    .filter((ev) => (filter === "ALL" ? true : ev.side === filter));

  return (
    <Card className="flex flex-col h-full overflow-hidden">
      <CardHeader className="flex-row items-center justify-between space-y-0 pb-3 border-b border-border/70">
        <div className="flex items-center gap-2">
          <History className="h-4 w-4 text-indigo-400" />
          <CardTitle className="text-xs uppercase tracking-wider text-muted-foreground">
            Trade Activity Log
          </CardTitle>
        </div>
        <Badge variant="outline" className="font-mono">
          {events.length} trades
        </Badge>
      </CardHeader>

      {/* Filter Bar */}
      <div className="flex items-center gap-1 px-3 py-2 border-b border-border/50 bg-muted/20">
        {(["ALL", "BUY", "SELL"] as const).map((side) => (
          <button
            key={side}
            type="button"
            onClick={() => setFilter(side)}
            className={`rounded-md px-2.5 py-1 text-[11px] font-semibold transition-colors ${
              filter === side
                ? "bg-background text-foreground shadow-sm border border-border"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            {side}
          </button>
        ))}
      </div>

      <CardContent className="p-0 flex-1 min-h-0">
        <ScrollArea className="h-[440px] xl:h-[520px]">
          {displayed.length === 0 ? (
            <div className="flex h-40 items-center justify-center text-xs text-muted-foreground">
              No {filter === "ALL" ? "" : filter} trade events recorded.
            </div>
          ) : (
            <Table>
              <TableHeader className="sticky top-0 bg-card z-10">
                <TableRow>
                  <TableHead>Date</TableHead>
                  <TableHead>Signal</TableHead>
                  <TableHead className="text-right">Price</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {displayed.map((ev, idx) => (
                  <TableRow key={`${ev.time}-${idx}`}>
                    <TableCell className="font-mono text-[11px] text-muted-foreground whitespace-nowrap">
                      {ev.time}
                    </TableCell>
                    <TableCell>
                      <Badge variant={ev.side === "BUY" ? "success" : "destructive"} className="gap-1 font-mono">
                        {ev.side === "BUY" ? (
                          <ArrowUpRight className="h-3 w-3" />
                        ) : (
                          <ArrowDownLeft className="h-3 w-3" />
                        )}
                        {ev.action}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right font-mono font-medium whitespace-nowrap">
                      {formatCurrency(ev.price, currency)}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </ScrollArea>
      </CardContent>
    </Card>
  );
};
