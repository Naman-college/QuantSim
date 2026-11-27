// Shourya/src/components/dashboard/ComparisonDashboard.tsx - Tab 2 ShadCN Multi-Strategy Leaderboard fitting 100% in frame.
// Member: Shourya (UI).

import React from "react";
import { Award, Layers, Shield, Sparkles, Trophy } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { ComparisonChart } from "@prakshat/ComparisonChart";
import { formatCurrency, type ComparisonResponse } from "@prakshat/chartTransformers";

interface ComparisonDashboardProps {
  data: ComparisonResponse | null;
  isDark: boolean;
  isLoading: boolean;
}

export const ComparisonDashboard: React.FC<ComparisonDashboardProps> = ({ data, isDark, isLoading }) => {
  const rankings = data?.ranking ?? [];
  const winner = rankings[0];
  const safest = rankings.length > 0 ? [...rankings].sort((a, b) => Math.abs(a.max_drawdown) - Math.abs(b.max_drawdown))[0] : null;
  const bestSharpe = rankings.length > 0 ? [...rankings].sort((a, b) => b.sharpe - a.sharpe)[0] : null;

  return (
    <div className="flex flex-col gap-3 h-full min-h-0 overflow-hidden">
      {/* 1. Top 4 Comparative Summary Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-2.5 shrink-0">
        {[
          {
            label: "Top Strategy Return",
            value: winner ? `${winner.total_return >= 0 ? "+" : ""}${winner.total_return.toFixed(2)}%` : "—",
            sub: winner ? `Winner: ${winner.strategy}` : "Waiting for run",
            icon: Trophy,
            accent: "text-emerald-500",
          },
          {
            label: "Lowest Drawdown",
            value: safest ? `${safest.max_drawdown.toFixed(2)}%` : "—",
            sub: safest ? `Safest: ${safest.strategy}` : "—",
            icon: Shield,
            accent: "text-sky-400",
          },
          {
            label: "Best Sharpe Ratio",
            value: bestSharpe ? bestSharpe.sharpe.toFixed(2) : "—",
            sub: bestSharpe ? `Best Risk-Adj: ${bestSharpe.strategy}` : "—",
            icon: Award,
            accent: "text-indigo-400",
          },
          {
            label: "Strategies Evaluated",
            value: rankings.length > 0 ? `${rankings.length} of 5 Done` : "—",
            sub: data ? `Asset: ${data.ticker}` : "All Strategies",
            icon: Layers,
            accent: "text-amber-400",
          },
        ].map((card) => {
          const Icon = card.icon;
          return (
            <Card key={card.label}>
              <CardContent className="p-3">
                {isLoading || !data ? (
                  <div className="space-y-1.5">
                    <Skeleton className="h-3 w-20" />
                    <Skeleton className="h-6 w-24" />
                    <Skeleton className="h-3 w-32" />
                  </div>
                ) : (
                  <>
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
                        {card.label}
                      </span>
                      <Icon className={`h-3.5 w-3.5 ${card.accent}`} />
                    </div>
                    <div className={`mt-1 text-base sm:text-lg xl:text-xl font-bold font-mono truncate ${card.accent}`}>
                      {card.value}
                    </div>
                    <p className="mt-0.5 truncate text-[10px] text-muted-foreground">{card.sub}</p>
                  </>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* 2. Chart + Ranked Leaderboard Grid (Locked inside remaining height at any shape) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 grid-rows-[1fr_minmax(150px,42%)] lg:grid-rows-1 gap-3 flex-1 min-h-0 overflow-hidden">
        {/* Left 7 cols: Prakshat's TradingView 5-Curve Overlay Chart */}
        <div className="lg:col-span-7 h-full min-h-0 overflow-hidden">
          <ComparisonChart data={data} isDark={isDark} isLoading={isLoading} />
        </div>

        {/* Right 5 cols: ShadCN Strategy Leaderboard + Key Takeaway */}
        <Card className="lg:col-span-5 flex flex-col h-full min-h-0 overflow-hidden">
          <CardHeader className="flex-row items-center justify-between space-y-0 px-3 py-2.5 border-b border-border/70 shrink-0">
            <CardTitle className="text-[11px] uppercase tracking-wider text-muted-foreground">
              Strategy Leaderboard
            </CardTitle>
            {winner && <Badge variant="success">Top: {winner.strategy.replace(/^\d+\.\s*/, "")}</Badge>}
          </CardHeader>

          <CardContent className="p-0 flex-1 min-h-0 overflow-y-auto">
            <Table>
              <TableHeader className="sticky top-0 bg-card z-10 shadow-[0_1px_0_0_hsl(var(--border))]">
                <TableRow>
                  <TableHead className="h-8 px-2 w-10">#</TableHead>
                  <TableHead className="h-8 px-2">Strategy</TableHead>
                  <TableHead className="h-8 px-2 text-right">Return</TableHead>
                  <TableHead className="h-8 px-2 text-right">CAGR</TableHead>
                  <TableHead className="h-8 px-2 text-right">Sharpe</TableHead>
                  <TableHead className="h-8 px-2 text-right">Max DD</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {rankings.map((row) => (
                  <TableRow key={row.strategy}>
                    <TableCell className="py-2 px-2">
                      <Badge variant={row.rank === 1 ? "success" : "outline"} className="font-mono text-[10px]">
                        #{row.rank}
                      </Badge>
                    </TableCell>
                    <TableCell className="py-2 px-2">
                      <div className="flex items-center gap-1.5">
                        <span className="h-2 w-2 rounded-full shrink-0" style={{ backgroundColor: row.color }} />
                        <div className="flex flex-col min-w-0">
                          <span className="font-medium text-foreground text-[11px] truncate">{row.strategy}</span>
                          <span className="text-[10px] font-mono text-muted-foreground truncate">
                            {formatCurrency(row.final_balance, data?.currency || "$")} · {row.trades} trades
                          </span>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell
                      className={`py-2 px-2 text-right font-mono text-[11px] font-semibold whitespace-nowrap ${
                        row.total_return >= 0 ? "text-emerald-500" : "text-rose-500"
                      }`}
                    >
                      {row.total_return >= 0 ? "+" : ""}
                      {row.total_return.toFixed(2)}%
                    </TableCell>
                    <TableCell className="py-2 px-2 text-right font-mono text-[11px] text-muted-foreground whitespace-nowrap">
                      {row.cagr >= 0 ? "+" : ""}
                      {row.cagr.toFixed(1)}%
                    </TableCell>
                    <TableCell className="py-2 px-2 text-right font-mono text-[11px] font-medium whitespace-nowrap">
                      {row.sharpe.toFixed(2)}
                    </TableCell>
                    <TableCell className="py-2 px-2 text-right font-mono text-[11px] text-rose-500 whitespace-nowrap">
                      {row.max_drawdown.toFixed(1)}%
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>

          {/* Quant Takeaway Callout pinned at card bottom */}
          {winner && safest && (
            <div className="m-2.5 rounded-lg border border-indigo-500/30 bg-indigo-500/10 p-2.5 shrink-0">
              <div className="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wider text-indigo-400">
                <Sparkles className="h-3 w-3" />
                Key Quant Takeaway
              </div>
              <p className="mt-1 text-[11px] leading-snug text-muted-foreground">
                Top performer for <span className="font-mono font-semibold text-foreground">{data?.ticker}</span> is{" "}
                <span className="font-semibold text-foreground">{winner.strategy}</span> ({winner.total_return >= 0 ? "+" : ""}
                {winner.total_return.toFixed(1)}%). Safest profile:{" "}
                <span className="font-semibold text-foreground">{safest.strategy}</span> (MDD{" "}
                <span className="font-mono text-rose-400">{safest.max_drawdown.toFixed(1)}%</span>).
              </p>
            </div>
          )}
        </Card>
      </div>
    </div>
  );
};
