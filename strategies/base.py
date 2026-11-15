"""
base.py - Base definition and common helper utilities for all strategies.
Maintained by Member 3 (Strategy Developer).
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np
from core.metrics import calculate_metrics, calculate_drawdown_series


class BaseStrategy(ABC):
    """
    Abstract base class for all trading strategies.
    Ensures every strategy has a consistent interface for the GUI and backtest engine.
    """
    name: str = "Base Strategy"
    description: str = "Strategy description"

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
        pass

    @staticmethod
    def extract_trade_events(df: pd.DataFrame) -> list:
        """
        Finds exact dates where signal changed from 0 to 1 (BUY) or 1 to 0 (SELL).
        """
        events = []
        if 'Signal' not in df.columns:
            return events

        signals = df['Signal'].values
        closes = df['Close'].values
        dates = df.index

        prev_signal = 0
        for i in range(len(signals)):
            curr_signal = signals[i]
            if curr_signal == 1 and prev_signal == 0:
                events.append((dates[i], closes[i], "BUY"))
            elif curr_signal == 0 and prev_signal == 1:
                events.append((dates[i], closes[i], "SELL"))
            prev_signal = curr_signal

        return events
