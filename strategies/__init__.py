"""
strategies/__init__.py - Exposes the 5 selected trading strategies.
"""

from strategies.lump_sum import LumpSumStrategy
from strategies.buying_dips import BuyingDipsStrategy
from strategies.sip import SIPStrategy
from strategies.target_stop_loss import TargetStopLossStrategy
from strategies.moving_average import MovingAverageCrossoverStrategy

AVAILABLE_STRATEGIES = {
    "1. Lump Sum Investment": LumpSumStrategy(),
    "2. Buying Dips": BuyingDipsStrategy(),
    "3. SIP (Systematic Investment Plan)": SIPStrategy(),
    "4. Target Gain & Stop Loss": TargetStopLossStrategy(),
    "5. Moving Average Crossover": MovingAverageCrossoverStrategy(),
}
