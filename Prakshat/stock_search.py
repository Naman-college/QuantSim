"""
Prakshat/stock_search.py - Offline curated watchlist + live Yahoo Finance Search API integration.
Member: Prakshat (Finance API and Charts API Integration).
"""

import urllib.request  # Built-in HTTP client used to call Yahoo Finance's autocomplete endpoint
import urllib.parse  # URL encoder to safely escape spaces and special characters in search queries
import json  # JSON parser for decoding the Yahoo Finance REST response
from typing import List, Dict  # Type annotations for structured search result lists
from Prakshat.presets import PRESET_MARKETS  # Reference to market presets (kept for shared domain awareness)

# Curated high-frequency watchlist (US & Indian equities/ETFs) for instant offline matching
CURATED_WATCHLIST: List[Dict[str, str]] = [
    # --- US MAJOR INDICES & KEY SECTOR ETFS ---
    {"symbol": "SPY", "name": "SPDR S&P 500 ETF Trust", "exchange": "NYSE Arca", "market": "US"},  # US S&P 500 benchmark ETF
    {"symbol": "QQQ", "name": "Invesco QQQ Trust (Nasdaq 100)", "exchange": "NASDAQ", "market": "US"},  # US Nasdaq 100 ETF
    {"symbol": "DIA", "name": "SPDR Dow Jones Industrial Average ETF", "exchange": "NYSE Arca", "market": "US"},  # Dow 30 ETF
    {"symbol": "IWM", "name": "iShares Russell 2000 ETF", "exchange": "NYSE Arca", "market": "US"},  # US Small-Cap ETF
    {"symbol": "VOO", "name": "Vanguard S&P 500 ETF", "exchange": "NYSE Arca", "market": "US"},  # Low-fee S&P 500 ETF
    {"symbol": "VTI", "name": "Vanguard Total Stock Market ETF", "exchange": "NYSE Arca", "market": "US"},  # Total US market ETF
    {"symbol": "GLD", "name": "SPDR Gold Shares", "exchange": "NYSE Arca", "market": "US"},  # Gold bullion ETF
    {"symbol": "TLT", "name": "iShares 20+ Year Treasury Bond ETF", "exchange": "NASDAQ", "market": "US"},  # Long-duration US bonds ETF
    {"symbol": "XLF", "name": "Financial Select Sector SPDR", "exchange": "NYSE Arca", "market": "US"},  # US Financials ETF
    {"symbol": "XLK", "name": "Technology Select Sector SPDR", "exchange": "NYSE Arca", "market": "US"},  # US Tech ETF
    {"symbol": "SOXX", "name": "iShares Semiconductor ETF", "exchange": "NASDAQ", "market": "US"},  # Semiconductor ETF
    {"symbol": "SMH", "name": "VanEck Semiconductor ETF", "exchange": "NASDAQ", "market": "US"},  # Semiconductor ETF
    # --- US MEGA-CAP & BLUECHIP LEADERS ---
    {"symbol": "AAPL", "name": "Apple Inc.", "exchange": "NASDAQ", "market": "US"},  # Apple Inc.
    {"symbol": "MSFT", "name": "Microsoft Corporation", "exchange": "NASDAQ", "market": "US"},  # Microsoft
    {"symbol": "NVDA", "name": "NVIDIA Corporation", "exchange": "NASDAQ", "market": "US"},  # NVIDIA
    {"symbol": "AMZN", "name": "Amazon.com, Inc.", "exchange": "NASDAQ", "market": "US"},  # Amazon
    {"symbol": "GOOGL", "name": "Alphabet Inc. (Class A)", "exchange": "NASDAQ", "market": "US"},  # Alphabet Class A
    {"symbol": "GOOG", "name": "Alphabet Inc. (Class C)", "exchange": "NASDAQ", "market": "US"},  # Alphabet Class C
    {"symbol": "META", "name": "Meta Platforms, Inc.", "exchange": "NASDAQ", "market": "US"},  # Meta Platforms
    {"symbol": "TSLA", "name": "Tesla, Inc.", "exchange": "NASDAQ", "market": "US"},  # Tesla
    {"symbol": "BRK-B", "name": "Berkshire Hathaway Inc.", "exchange": "NYSE", "market": "US"},  # Berkshire Hathaway
    {"symbol": "AVGO", "name": "Broadcom Inc.", "exchange": "NASDAQ", "market": "US"},  # Broadcom
    {"symbol": "JPM", "name": "JPMorgan Chase & Co.", "exchange": "NYSE", "market": "US"},  # JPMorgan
    {"symbol": "LLY", "name": "Eli Lilly and Company", "exchange": "NYSE", "market": "US"},  # Eli Lilly
    {"symbol": "V", "name": "Visa Inc.", "exchange": "NYSE", "market": "US"},  # Visa
    {"symbol": "UNH", "name": "UnitedHealth Group Incorporated", "exchange": "NYSE", "market": "US"},  # UnitedHealth
    {"symbol": "MA", "name": "Mastercard Incorporated", "exchange": "NYSE", "market": "US"},  # Mastercard
    {"symbol": "COST", "name": "Costco Wholesale Corporation", "exchange": "NASDAQ", "market": "US"},  # Costco
    {"symbol": "PG", "name": "The Procter & Gamble Company", "exchange": "NYSE", "market": "US"},  # Procter & Gamble
    {"symbol": "HD", "name": "The Home Depot, Inc.", "exchange": "NYSE", "market": "US"},  # Home Depot
    {"symbol": "NFLX", "name": "Netflix, Inc.", "exchange": "NASDAQ", "market": "US"},  # Netflix
    {"symbol": "JNJ", "name": "Johnson & Johnson", "exchange": "NYSE", "market": "US"},  # Johnson & Johnson
    {"symbol": "BAC", "name": "Bank of America Corporation", "exchange": "NYSE", "market": "US"},  # Bank of America
    {"symbol": "WMT", "name": "Walmart Inc.", "exchange": "NYSE", "market": "US"},  # Walmart
    {"symbol": "ABBV", "name": "AbbVie Inc.", "exchange": "NYSE", "market": "US"},  # AbbVie
    {"symbol": "CRM", "name": "Salesforce, Inc.", "exchange": "NYSE", "market": "US"},  # Salesforce
    {"symbol": "ORCL", "name": "Oracle Corporation", "exchange": "NYSE", "market": "US"},  # Oracle
    {"symbol": "AMD", "name": "Advanced Micro Devices, Inc.", "exchange": "NASDAQ", "market": "US"},  # AMD
    {"symbol": "CVX", "name": "Chevron Corporation", "exchange": "NYSE", "market": "US"},  # Chevron
    {"symbol": "XOM", "name": "Exxon Mobil Corporation", "exchange": "NYSE", "market": "US"},  # Exxon Mobil
    {"symbol": "KO", "name": "The Coca-Cola Company", "exchange": "NYSE", "market": "US"},  # Coca-Cola
    {"symbol": "PEP", "name": "PepsiCo, Inc.", "exchange": "NASDAQ", "market": "US"},  # PepsiCo
    {"symbol": "MRK", "name": "Merck & Co., Inc.", "exchange": "NYSE", "market": "US"},  # Merck
    {"symbol": "ADBE", "name": "Adobe Inc.", "exchange": "NASDAQ", "market": "US"},  # Adobe
    {"symbol": "QCOM", "name": "QUALCOMM Incorporated", "exchange": "NASDAQ", "market": "US"},  # Qualcomm
    {"symbol": "CSCO", "name": "Cisco Systems, Inc.", "exchange": "NASDAQ", "market": "US"},  # Cisco
    {"symbol": "INTC", "name": "Intel Corporation", "exchange": "NASDAQ", "market": "US"},  # Intel
    {"symbol": "DIS", "name": "The Walt Disney Company", "exchange": "NYSE", "market": "US"},  # Disney
    {"symbol": "VZ", "name": "Verizon Communications Inc.", "exchange": "NYSE", "market": "US"},  # Verizon
    {"symbol": "NKE", "name": "NIKE, Inc.", "exchange": "NYSE", "market": "US"},  # Nike
    # --- INDIAN INDICES (NSE & BSE) ---
    {"symbol": "^NSEI", "name": "NIFTY 50 Index", "exchange": "NSE", "market": "India"},  # Nifty 50 Index
    {"symbol": "^BSESN", "name": "S&P BSE SENSEX", "exchange": "BSE", "market": "India"},  # BSE Sensex Index
    {"symbol": "^NSEBANK", "name": "NIFTY BANK Index", "exchange": "NSE", "market": "India"},  # Nifty Bank Index
    {"symbol": "^CNXIT", "name": "NIFTY IT Index", "exchange": "NSE", "market": "India"},  # Nifty IT Index
    # --- INDIAN NIFTY 50 & BLUECHIP LEADERS ---
    {"symbol": "RELIANCE.NS", "name": "Reliance Industries Limited", "exchange": "NSE", "market": "India"},  # Reliance
    {"symbol": "TCS.NS", "name": "Tata Consultancy Services Limited", "exchange": "NSE", "market": "India"},  # TCS
    {"symbol": "HDFCBANK.NS", "name": "HDFC Bank Limited", "exchange": "NSE", "market": "India"},  # HDFC Bank
    {"symbol": "INFY.NS", "name": "Infosys Limited", "exchange": "NSE", "market": "India"},  # Infosys
    {"symbol": "ICICIBANK.NS", "name": "ICICI Bank Limited", "exchange": "NSE", "market": "India"},  # ICICI Bank
    {"symbol": "BHARTIARTL.NS", "name": "Bharti Airtel Limited", "exchange": "NSE", "market": "India"},  # Bharti Airtel
    {"symbol": "SBIN.NS", "name": "State Bank of India", "exchange": "NSE", "market": "India"},  # SBI
    {"symbol": "LICI.NS", "name": "Life Insurance Corporation of India", "exchange": "NSE", "market": "India"},  # LIC
    {"symbol": "ITC.NS", "name": "ITC Limited", "exchange": "NSE", "market": "India"},  # ITC
    {"symbol": "HINDUNILVR.NS", "name": "Hindustan Unilever Limited", "exchange": "NSE", "market": "India"},  # HUL
    {"symbol": "LT.NS", "name": "Larsen & Toubro Limited", "exchange": "NSE", "market": "India"},  # L&T
    {"symbol": "BAJFINANCE.NS", "name": "Bajaj Finance Limited", "exchange": "NSE", "market": "India"},  # Bajaj Finance
    {"symbol": "HCLTECH.NS", "name": "HCL Technologies Limited", "exchange": "NSE", "market": "India"},  # HCL Tech
    {"symbol": "KOTAKBANK.NS", "name": "Kotak Mahindra Bank Limited", "exchange": "NSE", "market": "India"},  # Kotak Bank
    {"symbol": "AXISBANK.NS", "name": "Axis Bank Limited", "exchange": "NSE", "market": "India"},  # Axis Bank
    {"symbol": "SUNPHARMA.NS", "name": "Sun Pharmaceutical Industries", "exchange": "NSE", "market": "India"},  # Sun Pharma
    {"symbol": "TITAN.NS", "name": "Titan Company Limited", "exchange": "NSE", "market": "India"},  # Titan
    {"symbol": "MARUTI.NS", "name": "Maruti Suzuki India Limited", "exchange": "NSE", "market": "India"},  # Maruti Suzuki
    {"symbol": "TATASTEEL.NS", "name": "Tata Steel Limited", "exchange": "NSE", "market": "India"},  # Tata Steel
    {"symbol": "TATAPOWER.NS", "name": "Tata Power Company Limited", "exchange": "NSE", "market": "India"},  # Tata Power
    {"symbol": "TATACOMM.NS", "name": "Tata Communications Limited", "exchange": "NSE", "market": "India"},  # Tata Comm
    {"symbol": "ULTRACEMCO.NS", "name": "UltraTech Cement Limited", "exchange": "NSE", "market": "India"},  # UltraTech Cement
    {"symbol": "BAJAJFINSV.NS", "name": "Bajaj Finserv Limited", "exchange": "NSE", "market": "India"},  # Bajaj Finserv
    {"symbol": "BAJAJ-AUTO.NS", "name": "Bajaj Auto Limited", "exchange": "NSE", "market": "India"},  # Bajaj Auto
    {"symbol": "HEROMOTOCO.NS", "name": "Hero MotoCorp Limited", "exchange": "NSE", "market": "India"},  # Hero MotoCorp
    {"symbol": "NTPC.NS", "name": "NTPC Limited", "exchange": "NSE", "market": "India"},  # NTPC
    {"symbol": "ONGC.NS", "name": "Oil and Natural Gas Corporation", "exchange": "NSE", "market": "India"},  # ONGC
    {"symbol": "POWERGRID.NS", "name": "Power Grid Corporation of India", "exchange": "NSE", "market": "India"},  # Power Grid
    {"symbol": "ADANIENT.NS", "name": "Adani Enterprises Limited", "exchange": "NSE", "market": "India"},  # Adani Enterprises
    {"symbol": "ADANIPORTS.NS", "name": "Adani Ports and SEZ Limited", "exchange": "NSE", "market": "India"},  # Adani Ports
    {"symbol": "COALINDIA.NS", "name": "Coal India Limited", "exchange": "NSE", "market": "India"},  # Coal India
    {"symbol": "ASIANPAINT.NS", "name": "Asian Paints Limited", "exchange": "NSE", "market": "India"},  # Asian Paints
    {"symbol": "JSWSTEEL.NS", "name": "JSW Steel Limited", "exchange": "NSE", "market": "India"},  # JSW Steel
    {"symbol": "M&M.NS", "name": "Mahindra & Mahindra Limited", "exchange": "NSE", "market": "India"},  # M&M
    {"symbol": "WIPRO.NS", "name": "Wipro Limited", "exchange": "NSE", "market": "India"},  # Wipro
    {"symbol": "GRASIM.NS", "name": "Grasim Industries Limited", "exchange": "NSE", "market": "India"},  # Grasim
    {"symbol": "NESTLEIND.NS", "name": "Nestle India Limited", "exchange": "NSE", "market": "India"},  # Nestle India
    {"symbol": "TECHM.NS", "name": "Tech Mahindra Limited", "exchange": "NSE", "market": "India"},  # Tech Mahindra
    {"symbol": "HINDALCO.NS", "name": "Hindalco Industries Limited", "exchange": "NSE", "market": "India"},  # Hindalco
    {"symbol": "CIPLA.NS", "name": "Cipla Limited", "exchange": "NSE", "market": "India"},  # Cipla
    {"symbol": "DRREDDY.NS", "name": "Dr. Reddy's Laboratories", "exchange": "NSE", "market": "India"},  # Dr. Reddy's
    {"symbol": "EICHERMOT.NS", "name": "Eicher Motors Limited", "exchange": "NSE", "market": "India"},  # Eicher Motors
    {"symbol": "BPCL.NS", "name": "Bharat Petroleum Corporation", "exchange": "NSE", "market": "India"},  # BPCL
    {"symbol": "DIVISLAB.NS", "name": "Divi's Laboratories Limited", "exchange": "NSE", "market": "India"},  # Divi's Labs
    {"symbol": "SBILIFE.NS", "name": "SBI Life Insurance Company", "exchange": "NSE", "market": "India"},  # SBI Life
    {"symbol": "HDFCLIFE.NS", "name": "HDFC Life Insurance Company", "exchange": "NSE", "market": "India"},  # HDFC Life
    {"symbol": "BRITANNIA.NS", "name": "Britannia Industries Limited", "exchange": "NSE", "market": "India"},  # Britannia
    {"symbol": "APOLLOHOSP.NS", "name": "Apollo Hospitals Enterprise", "exchange": "NSE", "market": "India"},  # Apollo Hospitals
    {"symbol": "BEL.NS", "name": "Bharat Electronics Limited", "exchange": "NSE", "market": "India"},  # BEL
    {"symbol": "HAL.NS", "name": "Hindustan Aeronautics Limited", "exchange": "NSE", "market": "India"},  # HAL
    {"symbol": "TRENT.NS", "name": "Trent Limited", "exchange": "NSE", "market": "India"},  # Trent
    {"symbol": "VBL.NS", "name": "Varun Beverages Limited", "exchange": "NSE", "market": "India"},  # Varun Beverages
    {"symbol": "INDUSINDBK.NS", "name": "IndusInd Bank Limited", "exchange": "NSE", "market": "India"},  # IndusInd Bank
    {"symbol": "VEDL.NS", "name": "Vedanta Limited", "exchange": "NSE", "market": "India"},  # Vedanta
    {"symbol": "JIOFIN.NS", "name": "Jio Financial Services Limited", "exchange": "NSE", "market": "India"},  # Jio Financial
]


def search_local_watchlist(query: str, limit: int = 8) -> List[Dict[str, str]]:
    """Instant ranked substring matching against the local curated watchlist."""
    if not query:  # If query is empty, return the top default watchlist items
        return CURATED_WATCHLIST[:limit]  # Slice list up to requested limit

    q = query.strip().upper()  # Normalize query to uppercase for case-insensitive comparison
    matches = []  # Accumulator list preserving ranking priority

    for item in CURATED_WATCHLIST:  # Priority 1: Exact ticker symbol match (e.g., 'SPY')
        if item["symbol"].upper() == q:  # Exact equality check
            matches.append(item)  # Append highest-priority hit first

    for item in CURATED_WATCHLIST:  # Priority 2: Symbol starts with query prefix (e.g., 'TATA')
        if item not in matches and item["symbol"].upper().startswith(q):  # Avoid duplicates already added in Priority 1
            matches.append(item)  # Append prefix match

    for item in CURATED_WATCHLIST:  # Priority 3: Company name or symbol contains substring anywhere
        if item not in matches and (q in item["name"].upper() or q in item["symbol"].upper()):  # Substring check
            matches.append(item)  # Append lowest-priority match

    return matches[:limit]  # Cap returned results to 'limit'


def search_yahoo_online(query: str, limit: int = 8) -> List[Dict[str, str]]:
    """Queries Yahoo Finance's public autocomplete REST API for global stock symbols."""
    if not query or len(query.strip()) < 1:  # Skip network call on blank input
        return []  # Return empty list immediately

    url = f"https://query2.finance.yahoo.com/v1/finance/search?q={urllib.parse.quote(query)}&quotesCount={limit}&newsCount=0"  # Build Yahoo search URL with encoded query
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}  # Browser User-Agent header prevents HTTP 403 blocks from Yahoo

    try:
        req = urllib.request.Request(url, headers=headers)  # Construct HTTP GET request object
        with urllib.request.urlopen(req, timeout=3.5) as response:  # Open connection with 3.5s timeout so UI never hangs
            data = json.loads(response.read().decode("utf-8"))  # Read bytes, decode UTF-8, and parse JSON payload
            quotes = data.get("quotes", [])  # Extract 'quotes' array from Yahoo response
            results = []  # Normalized output list
            for q in quotes:  # Iterate over each returned security object
                sym = q.get("symbol")  # Read ticker symbol
                if not sym:  # Skip malformed entries lacking a symbol
                    continue
                name = q.get("shortname") or q.get("longname") or sym  # Prefer short name, fall back to long name or symbol
                exchange = q.get("exchange", "")  # Read exchange code (e.g., 'NMS', 'NSI')

                is_india = sym.endswith(".NS") or sym.endswith(".BO") or sym.startswith("^NSE") or sym.startswith("^BSE")  # Classify Indian vs US/Global market
                market = "India" if is_india else "US / Global"  # Assign human-readable market label

                results.append({  # Append standardized ticker dictionary matching CURATED_WATCHLIST schema
                    "symbol": sym,  # Stock ticker symbol
                    "name": name,  # Company/ETF display name
                    "exchange": exchange,  # Exchange identifier
                    "market": market  # Market region tag
                })
            return results  # Return parsed live results
    except Exception:
        return []  # Graceful offline fallback: return empty list if network is unavailable or times out


def search_stocks(query: str, limit: int = 10) -> List[Dict[str, str]]:
    """Hybrid search: checks instant local watchlist first, then supplements via Yahoo Finance API."""
    q = query.strip()  # Trim surrounding whitespace
    if not q:  # Return default top watchlist items when search bar is blank
        return CURATED_WATCHLIST[:limit]  # Slice top entries

    local = search_local_watchlist(q, limit=limit)  # Step 1: Run fast in-memory local search
    if len(local) >= 4:  # Short-circuit if local watchlist already gave 4+ strong matches (saves network latency)
        return local  # Return local matches immediately

    online = search_yahoo_online(q, limit=limit)  # Step 2: Hit Yahoo Finance online search for niche/unknown tickers
    seen = {item["symbol"].upper() for item in local}  # Track already-present symbols in a set for O(1) deduplication
    for item in online:  # Merge online results without duplicates
        if item["symbol"].upper() not in seen:  # Only add symbols not already in local hits
            local.append(item)  # Append online match
            seen.add(item["symbol"].upper())  # Record symbol in seen set
            if len(local) >= limit:  # Stop once total results reach the cap
                break

    return local[:limit]  # Return combined local + online suggestions
