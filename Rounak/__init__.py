"""
Rounak/__init__.py - Strategy registry exposing all 5 quantitative trading strategies.
Member: Rounak (Code for the Strategies).
"""

from Rounak.lump_sum import LumpSumStrategy  # Strategy 1: Buy & Hold baseline benchmark
from Rounak.buying_dips import BuyingDipsStrategy  # Strategy 2: Mean-reversion dip buyer
from Rounak.sip import SIPStrategy  # Strategy 3: Systematic Investment Plan (DCA)
from Rounak.target_stop_loss import TargetStopLossStrategy  # Strategy 4: Risk-managed Target & Stop-Loss
from Rounak.moving_average import MovingAverageCrossoverStrategy  # Strategy 5: Dual MA trend follower

# Master dictionary mapping UI display names to instantiated strategy objects
AVAILABLE_STRATEGIES = {
    "1. Lump Sum Investment": LumpSumStrategy(),  # Day-1 full/partial allocation strategy
    "2. Buying Dips": BuyingDipsStrategy(),  # Enters on single-day % drops and holds N days
    "3. SIP (Systematic Investment Plan)": SIPStrategy(),  # Monthly fixed-installment accumulation
    "4. Target Gain & Stop Loss": TargetStopLossStrategy(),  # Exits on profit target, stop loss, trailing stop, or timeout
    "5. Moving Average Crossover": MovingAverageCrossoverStrategy(),  # Golden Cross / Death Cross trend strategy
}
