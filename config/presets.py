"""
presets.py - Market presets, ticker universes, and default configurations.
Maintained by Member 1 (Data Ingestion & Watchlists).
"""

# Market Presets for US and Indian Markets
PRESET_MARKETS = {
    "US Equities & ETFs": {
        "S&P 500 ETF (SPY)": "SPY",
        "Nasdaq 100 ETF (QQQ)": "QQQ",
        "Apple Inc. (AAPL)": "AAPL",
        "Microsoft Corp. (MSFT)": "MSFT",
        "NVIDIA Corp. (NVDA)": "NVDA",
        "Tesla Inc. (TSLA)": "TSLA",
        "Amazon.com Inc. (AMZN)": "AMZN",
        "Alphabet Inc. (GOOGL)": "GOOGL",
        "Gold Trust ETF (GLD)": "GLD",
    },
    "Indian Markets (NSE)": {
        "NIFTY 50 Index": "^NSEI",
        "BSE SENSEX": "^BSESN",
        "Reliance Industries": "RELIANCE.NS",
        "Tata Consultancy Services": "TCS.NS",
        "HDFC Bank Ltd": "HDFCBANK.NS",
        "Infosys Ltd": "INFY.NS",
        "ICICI Bank Ltd": "ICICIBANK.NS",
        "Tata Motors Ltd": "TATAMOTORS.NS",
        "State Bank of India": "SBIN.NS",
    }
}

# Default Backtest Parameters
DEFAULT_INITIAL_CAPITAL = 10000.0
DEFAULT_START_DATE = "2020-01-01"
DEFAULT_BENCHMARK = "SPY"


def is_indian_ticker(ticker: str) -> bool:
    """Checks whether a ticker belongs to the Indian market (NSE/BSE)."""
    if not ticker:
        return False
    t = ticker.strip().upper()
    return (
        t.endswith(".NS") or
        t.endswith(".BO") or
        t.startswith("^NSE") or
        t.startswith("^BSE") or
        t in ["NSEI", "BSESN", "^NSEI", "^BSESN"]
    )


def get_currency_symbol(ticker: str) -> str:
    """Returns 'Rs. ' for Indian tickers and '$' for US/global tickers."""
    return "Rs. " if is_indian_ticker(ticker) else "$"
