// Shourya/src/components/dashboard/KpiGrid.tsx - 4 ShadCN KPI Cards with Radix Tooltips & Skeleton Loaders.
// Member: Shourya (UI).

import React from "react";
import { ArrowDownRight, ArrowUpRight, Info, ShieldCheck, TrendingUp, Wallet, Activity } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { formatCurrency } from "@prakshat/chartTransformers";

interface KpiGridProps {
  metrics: Record<string, number> | null; // Strategy KPIs from Naman/metrics.py
  benchMetrics: Record<string, number> | null; // Buy & Hold benchmark KPIs
  currency: string; // '$' or '₹'
  initialCapital: number; // Starting portfolio cash
  isLoading: boolean; // True while simulation is in flight
}

export const KpiGrid: React.FC<KpiGridProps> = ({
  metrics,
  benchMetrics,
  currency,
  initialCapital,
  isLoading,
}) => {
  const totRet = metrics?.["Total Return (%)"] ?? 0;
  const benchRet = benchMetrics?.["Total Return (%)"] ?? 0;
  const delta = totRet - benchRet;
  const cagr = metrics?.["CAGR (%)"] ?? 0;
  const mdd = metrics?.["Max Drawdown (%)"] ?? 0;
  const finalBal = metrics?.["Final Balance"] ?? initialCapital;
  const sharpe = metrics?.["Sharpe Ratio"] ?? 0;
  const vol = metrics?.["Annualized Volatility (%)"] ?? 0;
  const winRate = metrics?.["Win Rate (%)"] ?? 0;

  const cards = [
    {
      title: "Total Return",
      value: `${totRet >= 0 ? "+" : ""}${totRet.toFixed(2)}%`,
      sub: `vs Buy & Hold ${benchRet >= 0 ? "+" : ""}${benchRet.toFixed(1)}% (${delta >= 0 ? "+" : ""}${delta.toFixed(1)}%)`,
      positive: totRet >= 0,
      icon: TrendingUp,
      formula: "(Final Balance - Initial Capital) / Initial Capital × 100",
    },
    {
      title: "CAGR",
      value: `${cagr >= 0 ? "+" : ""}${cagr.toFixed(2)}%`,
      sub: `Sharpe ${sharpe.toFixed(2)} · Vol ${vol.toFixed(1)}%`,
      positive: cagr >= 0,
      icon: Activity,
      formula: "Compound Annual Growth Rate: (End / Start)^(1 / Years) - 1",
    },
    {
      title: "Max Drawdown",
      value: `${mdd.toFixed(2)}%`,
      sub: `Active Win Rate: ${winRate.toFixed(1)}%`,
      positive: mdd > -15,
      icon: ShieldCheck,
      formula: "Worst peak-to-trough percentage drop: min((Equity - Peak) / Peak)",
    },
    {
      title: "Final Balance",
      value: formatCurrency(finalBal, currency),
      sub: `From ${formatCurrency(initialCapital, currency)}`,
      positive: finalBal >= initialCapital,
      icon: Wallet,
      formula: "Mark-to-market ending portfolio value (Equity + Remaining Cash)",
    },
  ];

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-2.5 shrink-0">
      {cards.map((c) => {
        const Icon = c.icon;
        return (
          <Card key={c.title} className="relative overflow-hidden transition-colors hover:border-border/90">
            <CardContent className="p-3">
              {isLoading || !metrics ? (
                <div className="space-y-1.5">
                  <Skeleton className="h-3 w-20" />
                  <Skeleton className="h-6 w-28" />
                  <Skeleton className="h-3 w-32" />
                </div>
              ) : (
                <>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-1">
                      <span className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
                        {c.title}
                      </span>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <button type="button" className="text-muted-foreground/60 hover:text-foreground">
                            <Info className="h-3 w-3" />
                          </button>
                        </TooltipTrigger>
                        <TooltipContent>{c.formula}</TooltipContent>
                      </Tooltip>
                    </div>
                    <div
                      className={`flex h-5 w-5 items-center justify-center rounded-md ${
                        c.positive ? "bg-emerald-500/10 text-emerald-500" : "bg-rose-500/10 text-rose-500"
                      }`}
                    >
                      <Icon className="h-3 w-3" />
                    </div>
                  </div>

                  <div className="mt-1 flex items-baseline gap-1">
                    <span
                      className={`text-base sm:text-lg xl:text-xl font-bold tracking-tight font-mono truncate ${
                        c.positive ? "text-emerald-500" : "text-rose-500"
                      }`}
                    >
                      {c.value}
                    </span>
                    {c.positive ? (
                      <ArrowUpRight className="h-3.5 w-3.5 text-emerald-500 shrink-0" />
                    ) : (
                      <ArrowDownRight className="h-3.5 w-3.5 text-rose-500 shrink-0" />
                    )}
                  </div>

                  <p className="mt-0.5 truncate text-[10px] text-muted-foreground font-mono">{c.sub}</p>
                </>
              )}
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
};
