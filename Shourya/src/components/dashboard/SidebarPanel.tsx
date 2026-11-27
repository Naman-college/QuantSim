// Shourya/src/components/dashboard/SidebarPanel.tsx - Left ShadCN Control Sidebar for Asset, Strategy & Risk Settings.
// Member: Shourya (UI).

import React from "react";
import { Calendar, DollarSign, IndianRupee, Layers, Play, Search, SlidersHorizontal } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import { Separator } from "@/components/ui/separator";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ScrollArea } from "@/components/ui/scroll-area";

export interface StrategyConfigState {
  // Strategy 1: Lump Sum
  lumpAllocationPct: number;
  lumpCashYieldPct: number;
  lumpFeePct: number;
  // Strategy 2: Buying Dips
  dipPct: number;
  dipWindow: number;
  dipHoldDays: number;
  dipTakeProfitPct: number;
  dipStopLossPct: number;
  dipFeePct: number;
  // Strategy 3: SIP
  sipAmount: number;
  sipFrequency: "Monthly" | "Bi-Weekly" | "Weekly";
  sipStepUpPct: number;
  sipDipBoostPct: number;
  sipFeePct: number;
  // Strategy 4: Target Gain & Stop Loss
  targetGainPct: number;
  stopLossPct: number;
  trailingStop: boolean;
  trailingStopPct: number;
  maxHoldDays: number;
  cooldownDays: number;
  tslFeePct: number;
  // Strategy 5: Moving Average Crossover
  maFast: number;
  maSlow: number;
  maType: "SMA" | "EMA";
  useTrendFilter: boolean;
  trendFilterPeriod: number;
  maStopLossPct: number;
  maFeePct: number;
}

export const STRATEGY_NAMES = [
  "1. Lump Sum Investment",
  "2. Buying Dips",
  "3. SIP (Systematic Investment Plan)",
  "4. Target Gain & Stop Loss",
  "5. Moving Average Crossover",
];

interface SidebarPanelProps {
  selectedSymbol: string;
  selectedName: string;
  currency: string;
  strategyName: string;
  capital: number;
  startDate: string;
  config: StrategyConfigState;
  isRunning: boolean;
  onOpenSearch: () => void;
  onStrategyChange: (name: string) => void;
  onCapitalChange: (val: number) => void;
  onStartDateChange: (val: string) => void;
  onConfigChange: (patch: Partial<StrategyConfigState>) => void;
  onRunBacktest: () => void;
  onCompareAll: () => void;
}

export const SidebarPanel: React.FC<SidebarPanelProps> = ({
  selectedSymbol,
  selectedName,
  currency,
  strategyName,
  capital,
  startDate,
  config,
  isRunning,
  onOpenSearch,
  onStrategyChange,
  onCapitalChange,
  onStartDateChange,
  onConfigChange,
  onRunBacktest,
  onCompareAll,
}) => {
  const isIndia = currency === "₹";

  return (
    <aside className="w-full lg:w-[320px] xl:w-[340px] shrink-0 border-r border-border bg-card/50 flex flex-col">
      <ScrollArea className="flex-1">
        <div className="p-4 space-y-4">
          {/* 1. Active Asset Card */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label className="uppercase tracking-wider text-[11px]">Active Asset</Label>
              <button
                type="button"
                onClick={onOpenSearch}
                className="inline-flex items-center gap-1 text-[11px] font-medium text-primary hover:underline"
              >
                <Search className="h-3 w-3" /> Change (Ctrl+K)
              </button>
            </div>
            <Card
              onClick={onOpenSearch}
              className="cursor-pointer transition-colors hover:border-primary/50 bg-background/70"
            >
              <CardContent className="p-3 flex items-center justify-between gap-2">
                <div className="flex items-center gap-2.5 min-w-0">
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
                    {isIndia ? <IndianRupee className="h-4 w-4" /> : <DollarSign className="h-4 w-4" />}
                  </div>
                  <div className="min-w-0">
                    <div className="font-mono text-sm font-bold text-foreground truncate">{selectedSymbol}</div>
                    <div className="text-[11px] text-muted-foreground truncate">{selectedName}</div>
                  </div>
                </div>
                <Badge variant={isIndia ? "success" : "indigo"} className="shrink-0">
                  {isIndia ? "₹ INR" : "$ USD"}
                </Badge>
              </CardContent>
            </Card>
          </div>

          <Separator />

          {/* 2. Trading Strategy Selector */}
          <div className="space-y-2">
            <Label className="uppercase tracking-wider text-[11px]">Trading Strategy</Label>
            <Select value={strategyName} onValueChange={onStrategyChange}>
              <SelectTrigger>
                <SelectValue placeholder="Select a strategy" />
              </SelectTrigger>
              <SelectContent>
                {STRATEGY_NAMES.map((name) => (
                  <SelectItem key={name} value={name}>
                    {name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* 3. Strategy-Specific Controls */}
          <Card className="bg-background/60">
            <CardContent className="p-3.5 space-y-3">
              <div className="flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
                <SlidersHorizontal className="h-3.5 w-3.5 text-primary" />
                Strategy Parameters
              </div>

              {/* Strategy 1: Lump Sum */}
              {strategyName.startsWith("1.") && (
                <div className="space-y-3">
                  <div className="space-y-1.5">
                    <div className="flex justify-between text-xs">
                      <Label>Equity Allocation</Label>
                      <span className="font-mono font-semibold text-foreground">{config.lumpAllocationPct}%</span>
                    </div>
                    <Slider
                      value={[config.lumpAllocationPct]}
                      min={10}
                      max={100}
                      step={5}
                      onValueChange={([v]) => onConfigChange({ lumpAllocationPct: v })}
                    />
                  </div>
                  <Accordion type="single" collapsible>
                    <AccordionItem value="adv" className="border-none">
                      <AccordionTrigger className="py-1.5">Advanced Cash &amp; Fee</AccordionTrigger>
                      <AccordionContent>
                        <div className="grid grid-cols-2 gap-2">
                          <div className="space-y-1">
                            <Label>Cash Yield (%)</Label>
                            <Input
                              type="number"
                              step="0.5"
                              value={config.lumpCashYieldPct}
                              onChange={(e) => onConfigChange({ lumpCashYieldPct: Number(e.target.value) || 0 })}
                              className="h-8 font-mono text-xs"
                            />
                          </div>
                          <div className="space-y-1">
                            <Label>Fee (%)</Label>
                            <Input
                              type="number"
                              step="0.05"
                              value={config.lumpFeePct}
                              onChange={(e) => onConfigChange({ lumpFeePct: Number(e.target.value) || 0 })}
                              className="h-8 font-mono text-xs"
                            />
                          </div>
                        </div>
                      </AccordionContent>
                    </AccordionItem>
                  </Accordion>
                </div>
              )}

              {/* Strategy 2: Buying Dips */}
              {strategyName.startsWith("2.") && (
                <div className="space-y-3">
                  <div className="space-y-1.5">
                    <div className="flex justify-between text-xs">
                      <Label>Dip Trigger Drop</Label>
                      <span className="font-mono font-semibold text-rose-400">-{config.dipPct.toFixed(1)}%</span>
                    </div>
                    <Slider
                      value={[config.dipPct]}
                      min={0.5}
                      max={15}
                      step={0.5}
                      onValueChange={([v]) => onConfigChange({ dipPct: v })}
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    <div className="space-y-1">
                      <Label>Lookback (d)</Label>
                      <Input
                        type="number"
                        min={1}
                        max={30}
                        value={config.dipWindow}
                        onChange={(e) => onConfigChange({ dipWindow: Math.max(1, Number(e.target.value) || 1) })}
                        className="h-8 font-mono text-xs"
                      />
                    </div>
                    <div className="space-y-1">
                      <Label>Hold Days</Label>
                      <Input
                        type="number"
                        min={1}
                        max={90}
                        value={config.dipHoldDays}
                        onChange={(e) => onConfigChange({ dipHoldDays: Math.max(1, Number(e.target.value) || 10) })}
                        className="h-8 font-mono text-xs"
                      />
                    </div>
                  </div>
                  <Accordion type="single" collapsible>
                    <AccordionItem value="adv" className="border-none">
                      <AccordionTrigger className="py-1.5">Risk Exits &amp; Fee</AccordionTrigger>
                      <AccordionContent>
                        <div className="grid grid-cols-3 gap-2">
                          <div className="space-y-1">
                            <Label>TP (%)</Label>
                            <Input
                              type="number"
                              step="0.5"
                              value={config.dipTakeProfitPct}
                              onChange={(e) => onConfigChange({ dipTakeProfitPct: Number(e.target.value) || 0 })}
                              className="h-8 font-mono text-xs"
                            />
                          </div>
                          <div className="space-y-1">
                            <Label>SL (%)</Label>
                            <Input
                              type="number"
                              step="0.5"
                              value={config.dipStopLossPct}
                              onChange={(e) => onConfigChange({ dipStopLossPct: Number(e.target.value) || 0 })}
                              className="h-8 font-mono text-xs"
                            />
                          </div>
                          <div className="space-y-1">
                            <Label>Fee (%)</Label>
                            <Input
                              type="number"
                              step="0.05"
                              value={config.dipFeePct}
                              onChange={(e) => onConfigChange({ dipFeePct: Number(e.target.value) || 0 })}
                              className="h-8 font-mono text-xs"
                            />
                          </div>
                        </div>
                      </AccordionContent>
                    </AccordionItem>
                  </Accordion>
                </div>
              )}

              {/* Strategy 3: SIP */}
              {strategyName.startsWith("3.") && (
                <div className="space-y-3">
                  <div className="space-y-1">
                    <Label>Installment Amount ({currency})</Label>
                    <Input
                      type="number"
                      min={10}
                      step={100}
                      value={config.sipAmount}
                      onChange={(e) => onConfigChange({ sipAmount: Math.max(10, Number(e.target.value) || 500) })}
                      className="h-8 font-mono text-xs"
                    />
                  </div>
                  <div className="space-y-1">
                    <Label>Frequency</Label>
                    <Select
                      value={config.sipFrequency}
                      onValueChange={(v) => onConfigChange({ sipFrequency: v as StrategyConfigState["sipFrequency"] })}
                    >
                      <SelectTrigger className="h-8">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Monthly">Monthly</SelectItem>
                        <SelectItem value="Bi-Weekly">Bi-Weekly</SelectItem>
                        <SelectItem value="Weekly">Weekly</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <Accordion type="single" collapsible>
                    <AccordionItem value="adv" className="border-none">
                      <AccordionTrigger className="py-1.5">Step-Up &amp; Dip Boost</AccordionTrigger>
                      <AccordionContent>
                        <div className="grid grid-cols-2 gap-2">
                          <div className="space-y-1">
                            <Label>Annual Step-Up %</Label>
                            <Input
                              type="number"
                              step="1"
                              value={config.sipStepUpPct}
                              onChange={(e) => onConfigChange({ sipStepUpPct: Number(e.target.value) || 0 })}
                              className="h-8 font-mono text-xs"
                            />
                          </div>
                          <div className="space-y-1">
                            <Label>Dip Boost %</Label>
                            <Input
                              type="number"
                              step="5"
                              value={config.sipDipBoostPct}
                              onChange={(e) => onConfigChange({ sipDipBoostPct: Number(e.target.value) || 0 })}
                              className="h-8 font-mono text-xs"
                            />
                          </div>
                        </div>
                      </AccordionContent>
                    </AccordionItem>
                  </Accordion>
                </div>
              )}

              {/* Strategy 4: Target Gain & Stop Loss */}
              {strategyName.startsWith("4.") && (
                <div className="space-y-3">
                  <div className="grid grid-cols-2 gap-2">
                    <div className="space-y-1">
                      <Label>Target Gain %</Label>
                      <Input
                        type="number"
                        step="0.5"
                        min={0.5}
                        value={config.targetGainPct}
                        onChange={(e) => onConfigChange({ targetGainPct: Math.max(0.5, Number(e.target.value) || 5) })}
                        className="h-8 font-mono text-xs text-emerald-500"
                      />
                    </div>
                    <div className="space-y-1">
                      <Label>Stop Loss %</Label>
                      <Input
                        type="number"
                        step="0.5"
                        min={0.5}
                        value={config.stopLossPct}
                        onChange={(e) => onConfigChange({ stopLossPct: Math.max(0.5, Number(e.target.value) || 3) })}
                        className="h-8 font-mono text-xs text-rose-500"
                      />
                    </div>
                  </div>
                  <div className="flex items-center justify-between pt-1">
                    <Label htmlFor="trailing-switch">Trailing Stop</Label>
                    <Switch
                      id="trailing-switch"
                      checked={config.trailingStop}
                      onCheckedChange={(checked) => onConfigChange({ trailingStop: checked })}
                    />
                  </div>
                  <Accordion type="single" collapsible>
                    <AccordionItem value="adv" className="border-none">
                      <AccordionTrigger className="py-1.5">Advanced Risk Controls</AccordionTrigger>
                      <AccordionContent>
                        <div className="grid grid-cols-3 gap-2">
                          <div className="space-y-1">
                            <Label>Trail %</Label>
                            <Input
                              type="number"
                              step="0.5"
                              value={config.trailingStopPct}
                              onChange={(e) => onConfigChange({ trailingStopPct: Number(e.target.value) || 2 })}
                              className="h-8 font-mono text-xs"
                            />
                          </div>
                          <div className="space-y-1">
                            <Label>Max Hold</Label>
                            <Input
                              type="number"
                              value={config.maxHoldDays}
                              onChange={(e) => onConfigChange({ maxHoldDays: Number(e.target.value) || 0 })}
                              className="h-8 font-mono text-xs"
                            />
                          </div>
                          <div className="space-y-1">
                            <Label>Cooldown</Label>
                            <Input
                              type="number"
                              value={config.cooldownDays}
                              onChange={(e) => onConfigChange({ cooldownDays: Number(e.target.value) || 0 })}
                              className="h-8 font-mono text-xs"
                            />
                          </div>
                        </div>
                      </AccordionContent>
                    </AccordionItem>
                  </Accordion>
                </div>
              )}

              {/* Strategy 5: Moving Average Crossover */}
              {strategyName.startsWith("5.") && (
                <div className="space-y-3">
                  <div className="grid grid-cols-2 gap-2">
                    <div className="space-y-1">
                      <Label>Fast Period</Label>
                      <Input
                        type="number"
                        min={3}
                        max={150}
                        value={config.maFast}
                        onChange={(e) => onConfigChange({ maFast: Math.max(2, Number(e.target.value) || 20) })}
                        className="h-8 font-mono text-xs"
                      />
                    </div>
                    <div className="space-y-1">
                      <Label>Slow Period</Label>
                      <Input
                        type="number"
                        min={5}
                        max={300}
                        value={config.maSlow}
                        onChange={(e) => onConfigChange({ maSlow: Math.max(5, Number(e.target.value) || 50) })}
                        className="h-8 font-mono text-xs"
                      />
                    </div>
                  </div>
                  <div className="space-y-1">
                    <Label>Moving Average Type</Label>
                    <Select
                      value={config.maType}
                      onValueChange={(v) => onConfigChange({ maType: v as "SMA" | "EMA" })}
                    >
                      <SelectTrigger className="h-8">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="SMA">SMA (Simple Moving Average)</SelectItem>
                        <SelectItem value="EMA">EMA (Exponential Moving Average)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="flex items-center justify-between pt-1">
                    <Label htmlFor="trend-switch">200-SMA Trend Filter</Label>
                    <Switch
                      id="trend-switch"
                      checked={config.useTrendFilter}
                      onCheckedChange={(checked) => onConfigChange({ useTrendFilter: checked })}
                    />
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* 4. Capital & Timeframe */}
          <div className="space-y-3">
            <Label className="uppercase tracking-wider text-[11px]">Timeframe &amp; Capital</Label>
            <div className="space-y-2">
              <div className="space-y-1">
                <Label>Initial Capital ({currency})</Label>
                <Input
                  type="number"
                  min={100}
                  step={1000}
                  value={capital}
                  onChange={(e) => onCapitalChange(Math.max(100, Number(e.target.value) || 10000))}
                  className="h-9 font-mono text-xs"
                />
              </div>
              <div className="space-y-1">
                <div className="flex items-center justify-between">
                  <Label className="flex items-center gap-1">
                    <Calendar className="h-3 w-3" /> Start Date
                  </Label>
                  <div className="flex gap-1">
                    {["2020-01-01", "2022-01-01", "2023-01-01"].map((d) => (
                      <button
                        key={d}
                        type="button"
                        onClick={() => onStartDateChange(d)}
                        className={`rounded px-1.5 py-0.5 text-[10px] font-mono border transition-colors ${
                          startDate === d
                            ? "border-primary/40 bg-primary/15 text-primary"
                            : "border-border text-muted-foreground hover:text-foreground"
                        }`}
                      >
                        {d.slice(0, 4)}
                      </button>
                    ))}
                  </div>
                </div>
                <Input
                  type="date"
                  value={startDate}
                  onChange={(e) => onStartDateChange(e.target.value)}
                  className="h-9 font-mono text-xs"
                />
              </div>
            </div>
          </div>
        </div>
      </ScrollArea>

      {/* Bottom Sticky Action Footer */}
      <div className="p-4 border-t border-border bg-card/90 space-y-2">
        <Button className="w-full font-semibold" onClick={onRunBacktest} disabled={isRunning}>
          <Play className="h-3.5 w-3.5 fill-current" />
          Run Single Backtest
        </Button>
        <Button variant="outline" className="w-full text-xs" onClick={onCompareAll} disabled={isRunning}>
          <Layers className="h-3.5 w-3.5 text-indigo-400" />
          Compare All 5 Strategies
        </Button>
      </div>
    </aside>
  );
};
