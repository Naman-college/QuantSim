"""
sip.py - Strategy 3: Systematic Investment Plan (SIP / Dollar Cost Averaging).
Maintained by Member 3 (Strategy Developer).

Academic Concepts Showcased:
- Capped capital allocation (investing only available cash pool)
- Periodic recurring investments with monthly triggers
- Realistic portfolio accounting: Total Value = (Shares * Price) + Remaining Cash
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
from strategies.base import BaseStrategy
from core.metrics import calculate_drawdown_series


class SIPStrategy(BaseStrategy):
    name = "3. SIP (Systematic Investment Plan)"
    description = "Invests a fixed amount periodically from available capital pool until fully invested."

    def run(
        self,
        df: pd.DataFrame,
        initial_capital: float = 10000.0,
        monthly_installment: float = 500.0,
        **params
    ) -> Dict[str, Any]:
        """
        Parameters:
            initial_capital (float): Total capital available to invest
            monthly_installment (float): Recurring installment amount invested each month
        """
        res = df.copy()
        res['Market_Return'] = res['Close'].pct_change().fillna(0.0)

        n = len(res)
        # Trigger on the first trading day of each month
        months = res.index.month
        is_trigger_day = np.zeros(n, dtype=bool)
        is_trigger_day[0] = True  # Day 1 is the 1st installment
        for i in range(1, n):
            if months[i] != months[i - 1]:
                is_trigger_day[i] = True

        shares_owned = np.zeros(n, dtype=float)
        invested_capital = np.zeros(n, dtype=float)
        portfolio_value = np.zeros(n, dtype=float)
        cash_series = np.zeros(n, dtype=float)
        trade_events = []

        total_shares = 0.0
        remaining_cash = float(initial_capital)
        total_invested = 0.0

        for i in range(n):
            close_price = float(res['Close'].iloc[i])
            date = res.index[i]

            # If trigger day and we still have cash left to invest
            if is_trigger_day[i] and remaining_cash > 0:
                # Invest up to available cash (can't invest more than we have)
                installment_to_add = min(float(monthly_installment), remaining_cash)
                shares = installment_to_add / close_price
                total_shares += shares
                remaining_cash -= installment_to_add
                total_invested += installment_to_add

                trade_events.append((date, close_price, f"BUY (+{installment_to_add:,.0f})"))

            shares_owned[i] = total_shares
            invested_capital[i] = total_invested
            cash_series[i] = remaining_cash
            # Total equity = value of shares owned + uninvested cash
            portfolio_value[i] = (total_shares * close_price) + remaining_cash

        res['Invested_Capital'] = invested_capital
        res['Cash'] = cash_series
        res['Equity'] = portfolio_value
        res['Signal'] = np.where(shares_owned > 0, 1, 0)
        res['Strategy_Return'] = res['Equity'].pct_change().fillna(0.0)
        res['Drawdown'] = calculate_drawdown_series(res['Equity'])

        final_portfolio_val = float(portfolio_value[-1])
        net_profit = final_portfolio_val - initial_capital
        total_return_pct = (net_profit / initial_capital) * 100.0 if initial_capital > 0 else 0.0

        # Maximum Drawdown from peak portfolio value
        peak = np.maximum.accumulate(portfolio_value)
        peak = np.where(peak == 0, 1e-9, peak)
        mdd_pct = min(0.0, float(np.min((portfolio_value - peak) / peak)) * 100.0)

        # Annualized return (CAGR)
        total_days = max((res.index[-1] - res.index[0]).days, 1)
        years = total_days / 365.25
        cagr_pct = ((final_portfolio_val / initial_capital) ** (1.0 / years) - 1.0) * 100.0 if (years > 0 and initial_capital > 0 and final_portfolio_val > 0) else 0.0

        metrics = {
            "Total Return (%)": round(total_return_pct, 2),
            "Total Invested": round(total_invested, 2),
            "Final Balance": round(final_portfolio_val, 2),
            "Net Profit": round(net_profit, 2),
            "CAGR (%)": round(cagr_pct, 2),
            "Max Drawdown (%)": round(mdd_pct, 2),
            "Installments Count": len(trade_events),
        }

        return {
            "df": res,
            "metrics": metrics,
            "trade_events": trade_events,
            "params": {
                "Capital Budget": f"{initial_capital:,.2f}",
                "Monthly Installment": f"{monthly_installment:,.2f}",
                "Total Invested": f"{total_invested:,.2f}",
            }
        }
