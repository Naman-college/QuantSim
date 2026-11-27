// Shourya/src/components/dashboard/ComparisonDashboard.tsx - Tab 2 ShadCN Multi-Strategy Leaderboard & Overlay View.
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
    <div className="flex flex-col gap-4 h-full">
      {/* 1. Top 4 Comparative Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-3">
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
              <CardContent className="p-4">
                {isLoading || !data ? (
                  <div className="space-y-2">
                    <Skeleton className="h-3.5 w-24" />
                    <Skeleton className="h-7 w-28" />
                    <Skeleton className="h-3 w-36" />
                  </div>
                ) : (
                  <>
                    <div className="flex items-center justify-between">
                      <span className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
                        {card.label}
                      </span>
                      <Icon className={`h-4 w-4 ${card.accent}`} />
                    </div>
                    <div className={`mt-1.5 text-xl font-bold font-mono ${card.accent}`}>{card.value}</div>
                    <p className="mt-1 truncate text-[11px] text-muted-foreground">{card.sub}</p>
                  </>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* 2. Chart + Ranked Leaderboard Grid */}
      <div className="grid grid-cols-1 xl:grid-cols-12 gap-4 flex-1 min-h-[480px]">
        {/* Left 7 cols: Prakshat's TradingView 5-Curve Overlay Chart */}
        <div className="xl:col-span-7 min-h-[420px]">
          <ComparisonChart data={data} isDark={isDark} isLoading={isLoading} />
        </div>

        {/* Right 5 cols: ShadCN Strategy Leaderboard + Key Takeaway */}
        <Card className="xl:col-span-5 flex flex-col justify-between overflow-hidden">
          <div>
            <CardHeader className="flex-row items-center justify-between space-y-0 pb-3 border-b border-border/70">
              <CardTitle className="text-xs uppercase tracking-wider text-muted-foreground">
                Strategy Leaderboard
              </CardTitle>
              {winner && <Badge variant="success">Top: {winner.strategy.replace(/^\d+\.\s*/, "")}</Badge>}
            </CardHeader>
            <CardContent className="p-0">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-12">#</TableHead>
                    <TableHead>Strategy</TableHead>
                    <TableHead className="text-right">Return</TableHead>
                    <TableHead className="text-right">CAGR</TableHead>
                    <TableHead className="text-right">Sharpe</TableHead>
                    <TableHead className="text-right">Max DD</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {rankings.map((row) => (
                    <TableRow key={row.strategy}>
                      <TableCell>
                        <Badge variant={row.rank === 1 ? "success" : "outline"} className="font-mono">
                          #{row.rank}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <span className="h-2.5 w-2.5 rounded-full shrink-0" style={{ backgroundColor: row.color }} />
                          <div className="flex flex-col">
                            <span className="font-medium text-foreground">{row.strategy}</span>
                            <span className="text-[10px] font-mono text-muted-foreground">
                              {formatCurrency(row.final_balance, data?.currency || "$")} · {row.trades} trades
                            </span>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell
                        className={`text-right font-mono font-semibold ${
                          row.total_return >= 0 ? "text-emerald-500" : "text-rose-500"
                        }`}
                      >
                        {row.total_return >= 0 ? "+" : ""}
                        {row.total_return.toFixed(2)}%
                      </TableCell>
                      <TableCell className="text-right font-mono text-muted-foreground">
                        {row.cagr >= 0 ? "+" : ""}
                        {row.cagr.toFixed(1)}%
                      </TableCell>
                      <TableCell className="text-right font-mono font-medium">{row.sharpe.toFixed(2)}</TableCell>
                      <TableCell className="text-right font-mono text-rose-500">{row.max_drawdown.toFixed(1)}%</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </div>

          {/* Quant Takeaway Callout */}
          {winner && safest && (
            <div className="m-4 rounded-lg border border-indigo-500/30 bg-indigo-500/10 p-3.5">
              <div className="flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-wider text-indigo-400">
                <Sparkles className="h-3.5 w-3.5" />
                Key Quant Takeaway
              </div>
              <p className="mt-1 text-xs leading-relaxed text-muted-foreground">
                Top performer for <span className="font-mono font-semibold text-foreground">{data?.ticker}</span> is{" "}
                <span className="font-semibold text-foreground">{winner.strategy}</span> ({winner.total_return >= 0 ? "+" : ""}
                {winner.total_return.toFixed(1)}%). Safest risk profile is{" "}
                <span className="font-semibold text-foreground">{safest.strategy}</span> with minimal drawdown of{" "}
                <span className="font-mono text-rose-400">{safest.max_drawdown.toFixed(1)}%</span>.
              </p>
            </div>
          )}
        </Card>
      </div>
    </div>
  );
};
