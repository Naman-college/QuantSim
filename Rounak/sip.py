"""
Rounak/sip.py - Strategy 3: Systematic Investment Plan (SIP / Dollar-Cost Averaging).
Member: Rounak (Code for the Strategies).

Academic Concepts Showcased:
- Capped capital pool deployment (never investing more than available initial_capital)
- Flexible periodic triggers (Monthly, Bi-Weekly, Weekly) with optional annual step-up & dip boost
- Share-count accounting: Portfolio Value = (Total Shares * Price) + Remaining Cash
"""

import pandas as pd  # Time-series DataFrame and DatetimeIndex calendar extraction
import numpy as np  # Pre-allocated arrays for shares, cash, equity, and drawdown
from typing import Dict, Any  # Return type hint
from Rounak.base import BaseStrategy  # Base strategy contract
from Naman.metrics import calculate_drawdown_series  # Shared drawdown helper


class SIPStrategy(BaseStrategy):
    name = "3. SIP (Systematic Investment Plan)"  # Strategy display name
    description = "Invests a fixed amount periodically from available capital pool until fully invested."

    def run(
        self,
        df: pd.DataFrame,
        initial_capital: float = 10000.0,
        monthly_installment: float = 500.0,
        frequency: str = "Monthly",
        step_up_pct: float = 0.0,
        dip_boost_pct: float = 0.0,
        transaction_fee_pct: float = 0.0,
        **params
    ) -> Dict[str, Any]:
        """
        Simulates periodic Dollar-Cost Averaging from a fixed cash budget (`initial_capital`).

        Parameters:
            initial_capital (float): Total cash budget available for SIP installments
            monthly_installment (float): Base installment amount deployed per cycle
            frequency (str): "Monthly", "Bi-Weekly", or "Weekly"
            step_up_pct (float): Annual % increase applied to installment size each new year
            dip_boost_pct (float): Extra % added to installment when stock drops >= 2% on trigger day
            transaction_fee_pct (float): Brokerage fee % deducted from each installment purchase
        """
        res = df.copy()  # Clone price DataFrame
        res['Market_Return'] = res['Close'].pct_change().fillna(0.0)  # Compute daily underlying stock return

        n = len(res)  # Number of trading days in backtest
        freq_norm = frequency.strip().lower()  # Normalize frequency string
        is_trigger_day = np.zeros(n, dtype=bool)  # Boolean mask of SIP purchase dates
        is_trigger_day[0] = True  # Always deploy the 1st installment on Day 0

        if freq_norm == "weekly":  # Trigger roughly every 5 trading days (1 market week)
            for i in range(5, n, 5):  # Step every 5 bars
                is_trigger_day[i] = True
        elif freq_norm == "bi-weekly":  # Trigger roughly every 10 trading days (2 market weeks)
            for i in range(10, n, 10):  # Step every 10 bars
                is_trigger_day[i] = True
        else:  # Default "Monthly": trigger on the first trading day of each calendar month
            months = res.index.month  # Extract month numbers (1-12)
            for i in range(1, n):  # Detect month transition
                if months[i] != months[i - 1]:
                    is_trigger_day[i] = True

        shares_owned = np.zeros(n, dtype=float)  # Tracks cumulative shares held on each day
        invested_capital = np.zeros(n, dtype=float)  # Tracks cumulative cash deployed into stock
        portfolio_value = np.zeros(n, dtype=float)  # Tracks total equity (shares value + remaining cash)
        cash_series = np.zeros(n, dtype=float)  # Tracks uninvested cash balance over time
        trade_events = []  # List of SIP BUY events

        total_shares = 0.0  # Running count of accumulated fractional shares
        remaining_cash = float(initial_capital)  # Cash pool starting at full initial_capital
        total_invested = 0.0  # Running sum of cash spent on shares
        start_year = res.index[0].year  # Base year used to calculate annual step-up compounding
        fee_ratio = max(0.0, float(transaction_fee_pct)) / 100.0  # Convert fee % to decimal

        for i in range(n):  # Step through each trading day chronologically
            close_price = float(res['Close'].iloc[i])  # Current day's closing share price
            date = res.index[i]  # Current day's Timestamp
            day_ret = float(res['Market_Return'].iloc[i])  # Today's stock percentage change

            if is_trigger_day[i] and remaining_cash > 0:  # Invest on trigger day while cash remains in pool
                years_elapsed = max(0, date.year - start_year)  # Years passed since start for annual step-up
                stepped_amt = float(monthly_installment) * ((1.0 + max(0.0, float(step_up_pct)) / 100.0) ** years_elapsed)  # Apply annual step-up
                if dip_boost_pct > 0 and day_ret <= -0.02:  # Boost installment if market dipped >= 2% today
                    stepped_amt *= (1.0 + float(dip_boost_pct) / 100.0)

                installment_to_add = min(stepped_amt, remaining_cash)  # Cap installment at available cash reserve
                net_after_fee = installment_to_add * (1.0 - fee_ratio)  # Subtract optional brokerage fee
                shares = net_after_fee / close_price  # Buy fractional shares at today's Close
                total_shares += shares  # Add purchased shares to running total
                remaining_cash -= installment_to_add  # Deduct deployed cash from reserve pool
                total_invested += installment_to_add  # Increment cumulative invested amount

                trade_events.append((date, close_price, f"BUY (+{installment_to_add:,.0f})"))  # Log SIP installment marker

            shares_owned[i] = total_shares  # Record cumulative share count for day i
            invested_capital[i] = total_invested  # Record cumulative invested capital for day i
            cash_series[i] = remaining_cash  # Record uninvested cash for day i
            portfolio_value[i] = (total_shares * close_price) + remaining_cash  # Mark-to-market equity = Shares * Price + Cash

        res['Invested_Capital'] = invested_capital  # Store invested capital column
        res['Cash'] = cash_series  # Store cash balance column
        res['Equity'] = portfolio_value  # Store total portfolio equity curve
        res['Signal'] = np.where(shares_owned > 0, 1, 0)  # Active signal once shares are owned
        res['Strategy_Return'] = res['Equity'].pct_change().fillna(0.0)  # Daily portfolio return including cash drag
        res['Drawdown'] = calculate_drawdown_series(res['Equity'])  # Underwater % drawdown curve

        final_portfolio_val = float(portfolio_value[-1])  # Final balance on last trading day
        net_profit = final_portfolio_val - initial_capital  # Profit relative to starting cash pool
        total_return_pct = (net_profit / initial_capital) * 100.0 if initial_capital > 0 else 0.0  # Overall % return

        peak = np.maximum.accumulate(portfolio_value)  # Running all-time high of portfolio equity
        peak = np.where(peak == 0, 1e-9, peak)  # Protect against division by zero
        mdd_pct = min(0.0, float(np.min((portfolio_value - peak) / peak)) * 100.0)  # Worst peak-to-trough drop (%)

        total_days = max((res.index[-1] - res.index[0]).days, 1)  # Calendar days spanned by backtest
        years = total_days / 365.25  # Convert calendar days to fractional years
        cagr_pct = ((final_portfolio_val / initial_capital) ** (1.0 / years) - 1.0) * 100.0 if (years > 0 and initial_capital > 0 and final_portfolio_val > 0) else 0.0  # Annualized CAGR

        clean_ret = res['Strategy_Return'].dropna()
        std_ret = clean_ret.std()
        sharpe_ratio = float((clean_ret.mean() / std_ret) * np.sqrt(252)) if std_ret > 0 and not np.isnan(std_ret) else 0.0
        annual_vol = float(std_ret * np.sqrt(252) * 100.0) if not np.isnan(std_ret) else 0.0

        metrics = {  # Return SIP-specific and standard comparison metrics
            "Total Return (%)": round(total_return_pct, 2),
            "Total Invested": round(total_invested, 2),
            "Final Balance": round(final_portfolio_val, 2),
            "Net Profit": round(net_profit, 2),
            "CAGR (%)": round(cagr_pct, 2),
            "Annualized Volatility (%)": round(annual_vol, 2),
            "Sharpe Ratio": round(sharpe_ratio, 2),
            "Max Drawdown (%)": round(mdd_pct, 2),
            "Installments Count": len(trade_events),
        }

        return {  # Standardized strategy output dict
            "df": res,
            "metrics": metrics,
            "trade_events": trade_events,
            "params": {
                "Capital Budget": f"{initial_capital:,.2f}",
                "Installment": f"{monthly_installment:,.2f} ({frequency})",
                "Annual Step-Up": f"+{step_up_pct:.1f}%" if step_up_pct > 0 else "Off",
                "Dip Boost": f"+{dip_boost_pct:.1f}%" if dip_boost_pct > 0 else "Off",
                "Total Invested": f"{total_invested:,.2f}",
            }
        }
