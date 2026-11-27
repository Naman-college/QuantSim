"""
Prakshat/presets.py - Market presets, ticker universes, and currency detection helpers.
Member: Prakshat (Finance API and Charts API Integration).
"""

# Dictionary mapping market regions to friendly display names and Yahoo Finance ticker symbols
PRESET_MARKETS = {
    "US Equities & ETFs": {  # Group of popular US ETFs and large-cap stocks
        "S&P 500 ETF (SPY)": "SPY",  # Tracks the S&P 500 index
        "Nasdaq 100 ETF (QQQ)": "QQQ",  # Tracks the Nasdaq 100 tech-heavy index
        "Apple Inc. (AAPL)": "AAPL",  # Apple NASDAQ ticker
        "Microsoft Corp. (MSFT)": "MSFT",  # Microsoft NASDAQ ticker
        "NVIDIA Corp. (NVDA)": "NVDA",  # NVIDIA NASDAQ ticker
        "Tesla Inc. (TSLA)": "TSLA",  # Tesla NASDAQ ticker
        "Amazon.com Inc. (AMZN)": "AMZN",  # Amazon NASDAQ ticker
        "Alphabet Inc. (GOOGL)": "GOOGL",  # Google Class A NASDAQ ticker
        "Gold Trust ETF (GLD)": "GLD",  # SPDR Gold commodity ETF
    },
    "Indian Markets (NSE)": {  # Group of NSE/BSE indices and bluechip Indian stocks
        "NIFTY 50 Index": "^NSEI",  # Yahoo Finance symbol for NSE Nifty 50 index
        "BSE SENSEX": "^BSESN",  # Yahoo Finance symbol for BSE Sensex index
        "Reliance Industries": "RELIANCE.NS",  # '.NS' suffix denotes National Stock Exchange of India
        "Tata Consultancy Services": "TCS.NS",  # TCS on NSE
        "HDFC Bank Ltd": "HDFCBANK.NS",  # HDFC Bank on NSE
        "Infosys Ltd": "INFY.NS",  # Infosys on NSE
        "ICICI Bank Ltd": "ICICIBANK.NS",  # ICICI Bank on NSE
        "Tata Motors Ltd": "TATAMOTORS.NS",  # Tata Motors on NSE
        "State Bank of India": "SBIN.NS",  # SBI on NSE
    }
}

DEFAULT_INITIAL_CAPITAL = 10000.0  # Default starting portfolio cash used across backtests
DEFAULT_START_DATE = "2020-01-01"  # Default historical start date in YYYY-MM-DD format
DEFAULT_BENCHMARK = "SPY"  # Default market benchmark symbol


def is_indian_ticker(ticker: str) -> bool:
    """Checks whether a ticker symbol belongs to an Indian exchange (NSE or BSE)."""
    if not ticker:  # Guard against None or empty string inputs
        return False  # Empty ticker cannot be an Indian symbol
    t = ticker.strip().upper()  # Normalize whitespace and casing for reliable suffix checks
    return (  # Return True if any Indian exchange suffix or index prefix matches
        t.endswith(".NS") or  # NSE equity suffix (e.g., RELIANCE.NS)
        t.endswith(".BO") or  # BSE equity suffix (e.g., RELIANCE.BO)
        t.startswith("^NSE") or  # NSE index prefix (e.g., ^NSEI, ^NSEBANK)
        t.startswith("^BSE") or  # BSE index prefix (e.g., ^BSESN)
        t in ["NSEI", "BSESN", "^NSEI", "^BSESN"]  # Also handle stripped index names without '^'
    )


def get_currency_symbol(ticker: str) -> str:
    """Returns '₹' for Indian tickers and '$' for US/global tickers."""
    return "₹" if is_indian_ticker(ticker) else "$"  # Return Indian Rupee symbol for NSE/BSE, Dollar otherwise
