# Rounak — Quantitative Trading Strategies

**Team Member:** Rounak  
**Assigned Module:** Code for the 5 Quantitative Investment & Trading Strategies

---

## 📁 Folder Contents

| File | Strategy / Purpose |
| :--- | :--- |
| `__init__.py` | Exposes `AVAILABLE_STRATEGIES` mapping strategy names to instantiated strategy objects. |
| `base.py` | Abstract Base Class `BaseStrategy` enforcing a consistent `run()` contract + `extract_trade_events()` helper. |
| `lump_sum.py` | **Strategy 1 — Lump Sum Investment**: Day-1 Buy & Hold benchmark with configurable equity allocation %, unallocated cash yield %, and transaction fee. |
| `buying_dips.py` | **Strategy 2 — Buying Dips**: Buys after a pullback $\ge$ `dip_pct`% over `dip_window` days, holds up to `hold_days`, with optional Take-Profit, Stop-Loss, and fees. |
| `sip.py` | **Strategy 3 — SIP (Systematic Investment Plan)**: Periodic Dollar-Cost Averaging (`Monthly`, `Bi-Weekly`, or `Weekly`) from a capped capital budget with optional annual step-up and dip boost. |
| `target_stop_loss.py` | **Strategy 4 — Target Gain & Stop Loss**: Risk-managed state machine with take-profit, hard stop-loss, trailing stop, max-hold timeout, and cooldown. |
| `moving_average.py` | **Strategy 5 — Moving Average Crossover**: Trend-following Golden Cross / Death Cross system supporting `SMA` or `EMA`, optional 200-SMA macro trend filter, and stop-loss. |

---

## 🔍 Shared Strategy Contract

Every strategy subclasses `BaseStrategy` (`base.py`) and returns:
- **`df`**: Price DataFrame augmented with `Market_Return`, `Signal` (`1` = invested, `0` = cash), `Strategy_Return`, `Equity`, `Drawdown`, and optional MA columns (`MA_Fast`, `MA_Slow`, `MA_Trend`).
- **`metrics`**: Financial KPI dictionary calculated via `Naman/metrics.py`.
- **`trade_events`**: List of `(date, price, action_label)` tuples plotted as markers on Prakshat's chart and listed in Shourya's `TradeLogPanel`.
- **`params`**: Human-readable configuration summary.

---

## 🎓 Teacher Viva / Oral Exam Prep (Likely Questions & Answers)

1. **Q: Why do you use `res['Signal'].shift(1)` when calculating `Strategy_Return`?**  
   **A:** To prevent **lookahead bias**. Because signals are computed using Day $t$'s closing price, shifting `Signal` by 1 bar ensures Day $t$'s decision only earns Day $t+1$'s market return.
2. **Q: Why does `BaseStrategy` use `ABC` and `@abstractmethod`?**  
   **A:** It enforces polymorphism—`BacktestEngine` can execute any strategy via `strategy.run(...)` without strategy-specific `if/else` branching.
3. **Q: How does `BuyingDipsStrategy` support multi-day pullbacks?**  
   **A:** Using `res['Close'].pct_change(periods=dip_window)` measures the cumulative percentage drop across `dip_window` trading days rather than just 1 day.
4. **Q: How does `SIPStrategy` handle annual step-ups and dip boosts?**  
   **A:** On each trigger day (`Monthly` / `Bi-Weekly` / `Weekly`), it scales the base installment by `(1 + step_up_pct/100) ** years_elapsed`, boosts it by `dip_boost_pct` if the asset dropped $\ge 2\%$ that day, and caps spending at `remaining_cash`.
5. **Q: Why does `MovingAverageCrossoverStrategy` expose `MA_Fast`, `MA_Slow`, and `MA_Trend` columns on `df`?**  
   **A:** `Prakshat/chart_serializer.py` extracts those columns so `SingleStrategyChart.tsx` overlays the exact Fast/Slow/Trend moving average lines on top of the OHLC candlesticks.
