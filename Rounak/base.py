"""
Rounak/base.py - Abstract Base Class (ABC) and shared trade-event extractor for all strategies.
Member: Rounak (Code for the Strategies).

Academic Concepts Showcased:
- Object-Oriented Programming (ABC & @abstractmethod enforcing a unified contract)
- Polymorphism: BacktestEngine calls strategy.run() uniformly on any strategy subclass
"""

from abc import ABC, abstractmethod  # Abstract Base Class tools to enforce interface compliance
from typing import Dict, Any  # Type annotations for structured return dictionaries
import pandas as pd  # DataFrame type for price history and signal columns


class BaseStrategy(ABC):
    """
    Abstract base class for all trading strategies.
    Ensures every strategy implements run() and returns the exact same output structure.
    """
    name: str = "Base Strategy"  # Human-readable strategy title overridden by subclasses
    description: str = "Strategy description"  # Short explanation shown in docs/UI

    @abstractmethod
    def run(self, df: pd.DataFrame, initial_capital: float = 10000.0, **params) -> Dict[str, Any]:
        """
        Executes the strategy calculation on the given historical price DataFrame.

        Returns:
            dict containing:
                - 'df': DataFrame with 'Close', 'Signal', 'Strategy_Return', 'Equity', 'Drawdown'
                - 'metrics': dictionary of performance KPIs
                - 'trade_events': list of (date, price, 'BUY' | 'SELL') tuples for plotting markers
        """
        pass  # Subclasses must implement their own simulation logic

    @staticmethod
    def extract_trade_events(df: pd.DataFrame) -> list:
        """
        Scans the binary 'Signal' column (0=Cash, 1=Invested) to detect entry/exit transitions.
        0 -> 1 emits a 'BUY' event; 1 -> 0 emits a 'SELL' event.
        """
        events = []  # Accumulator for (date, price, action_label) tuples
        if 'Signal' not in df.columns:  # Return empty list safely if Signal column is missing
            return events

        signals = df['Signal'].values  # Extract NumPy array of 0/1 positions for fast iteration
        closes = df['Close'].values  # Extract NumPy array of daily closing prices
        dates = df.index  # DatetimeIndex corresponding to each trading bar

        prev_signal = 0  # Assume portfolio starts out of the market (cash) before Day 0
        for i in range(len(signals)):  # Walk chronologically across all trading days
            curr_signal = signals[i]  # Position state on day i (1 = holding stock, 0 = cash)
            if curr_signal == 1 and prev_signal == 0:  # Transition from Cash -> Stock
                events.append((dates[i], closes[i], "BUY"))  # Record BUY trade marker
            elif curr_signal == 0 and prev_signal == 1:  # Transition from Stock -> Cash
                events.append((dates[i], closes[i], "SELL"))  # Record SELL trade marker
            prev_signal = curr_signal  # Advance state memory to current day

        return events  # Return chronological list of trade transitions
