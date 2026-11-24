"""
stock_search.py - Fast autocomplete and search for US and Indian stocks & ETFs.
Maintained by Member 1 (Data Ingestion) & Member 4 (UI/UX Developer).
"""

import urllib.request
import json
from typing import List, Dict, Tuple
from config.presets import PRESET_MARKETS

# Curated high-frequency watchlist for instant local offline matching (100+ assets)
CURATED_WATCHLIST: List[Dict[str, str]] = [
    # --- US MAJOR INDICES & KEY SECTOR ETFS ---
    {"symbol": "SPY", "name": "SPDR S&P 500 ETF Trust", "exchange": "NYSE Arca", "market": "US"},
    {"symbol": "QQQ", "name": "Invesco QQQ Trust (Nasdaq 100)", "exchange": "NASDAQ", "market": "US"},
    {"symbol": "DIA", "name": "SPDR Dow Jones Industrial Average ETF", "exchange": "NYSE Arca", "market": "US"},
    {"symbol": "IWM", "name": "iShares Russell 2000 ETF", "exchange": "NYSE Arca", "market": "US"},
    {"symbol": "VOO", "name": "Vanguard S&P 500 ETF", "exchange": "NYSE Arca", "market": "US"},
    {"symbol": "VTI", "name": "Vanguard Total Stock Market ETF", "exchange": "NYSE Arca", "market": "US"},
    {"symbol": "GLD", "name": "SPDR Gold Shares", "exchange": "NYSE Arca", "market": "US"},
    {"symbol": "TLT", "name": "iShares 20+ Year Treasury Bond ETF", "exchange": "NASDAQ", "market": "US"},
    {"symbol": "XLF", "name": "Financial Select Sector SPDR", "exchange": "NYSE Arca", "market": "US"},
    {"symbol": "XLK", "name": "Technology Select Sector SPDR", "exchange": "NYSE Arca", "market": "US"},
    {"symbol": "SOXX", "name": "iShares Semiconductor ETF", "exchange": "NASDAQ", "market": "US"},
    {"symbol": "SMH", "name": "VanEck Semiconductor ETF", "exchange": "NASDAQ", "market": "US"},
    # --- US MEGA-CAP & BLUECHIP LEADERS ---
    {"symbol": "AAPL", "name": "Apple Inc.", "exchange": "NASDAQ", "market": "US"},
    {"symbol": "MSFT", "name": "Microsoft Corporation", "exchange": "NASDAQ", "market": "US"},
    {"symbol": "NVDA", "name": "NVIDIA Corporation", "exchange": "NASDAQ", "market": "US"},
    {"symbol": "AMZN", "name": "Amazon.com, Inc.", "exchange": "NASDAQ", "market": "US"},
    {"symbol": "GOOGL", "name": "Alphabet Inc. (Class A)", "exchange": "NASDAQ", "market": "US"},
    {"symbol": "GOOG", "name": "Alphabet Inc. (Class C)", "exchange": "NASDAQ", "market": "US"},
    {"symbol": "META", "name": "Meta Platforms, Inc.", "exchange": "NASDAQ", "market": "US"},
    {"symbol": "TSLA", "name": "Tesla, Inc.", "exchange": "NASDAQ", "market": "US"},
    {"symbol": "BRK-B", "name": "Berkshire Hathaway Inc.", "exchange": "NYSE", "market": "US"},
    {"symbol": "AVGO", "name": "Broadcom Inc.", "exchange": "NASDAQ", "market": "US"},
    {"symbol": "JPM", "name": "JPMorgan Chase & Co.", "exchange": "NYSE", "market": "US"},
    {"symbol": "LLY", "name": "Eli Lilly and Company", "exchange": "NYSE", "market": "US"},
    {"symbol": "V", "name": "Visa Inc.", "exchange": "NYSE", "market": "US"},
    {"symbol": "UNH", "name": "UnitedHealth Group Incorporated", "exchange": "NYSE", "market": "US"},
    {"symbol": "MA", "name": "Mastercard Incorporated", "exchange": "NYSE", "market": "US"},
    {"symbol": "COST", "name": "Costco Wholesale Corporation", "exchange": "NASDAQ", "market": "US"},
    {"symbol": "PG", "name": "The Procter & Gamble Company", "exchange": "NYSE", "market": "US"},
    {"symbol": "HD", "name": "The Home Depot, Inc.", "exchange": "NYSE", "market": "US"},
    {"symbol": "NFLX", "name": "Netflix, Inc.", "exchange": "NASDAQ", "market": "US"},
    {"symbol": "JNJ", "name": "Johnson & Johnson", "exchange": "NYSE", "market": "US"},
    {"symbol": "BAC", "name": "Bank of America Corporation", "exchange": "NYSE", "market": "US"},
    {"symbol": "WMT", "name": "Walmart Inc.", "exchange": "NYSE", "market": "US"},
    {"symbol": "ABBV", "name": "AbbVie Inc.", "exchange": "NYSE", "market": "US"},
    {"symbol": "CRM", "name": "Salesforce, Inc.", "exchange": "NYSE", "market": "US"},
    {"symbol": "ORCL", "name": "Oracle Corporation", "exchange": "NYSE", "market": "US"},
    {"symbol": "AMD", "name": "Advanced Micro Devices, Inc.", "exchange": "NASDAQ", "market": "US"},
    {"symbol": "CVX", "name": "Chevron Corporation", "exchange": "NYSE", "market": "US"},
    {"symbol": "XOM", "name": "Exxon Mobil Corporation", "exchange": "NYSE", "market": "US"},
    {"symbol": "KO", "name": "The Coca-Cola Company", "exchange": "NYSE", "market": "US"},
    {"symbol": "PEP", "name": "PepsiCo, Inc.", "exchange": "NASDAQ", "market": "US"},
    {"symbol": "MRK", "name": "Merck & Co., Inc.", "exchange": "NYSE", "market": "US"},
    {"symbol": "ADBE", "name": "Adobe Inc.", "exchange": "NASDAQ", "market": "US"},
    {"symbol": "QCOM", "name": "QUALCOMM Incorporated", "exchange": "NASDAQ", "market": "US"},
    {"symbol": "CSCO", "name": "Cisco Systems, Inc.", "exchange": "NASDAQ", "market": "US"},
    {"symbol": "INTC", "name": "Intel Corporation", "exchange": "NASDAQ", "market": "US"},
    {"symbol": "DIS", "name": "The Walt Disney Company", "exchange": "NYSE", "market": "US"},
    {"symbol": "VZ", "name": "Verizon Communications Inc.", "exchange": "NYSE", "market": "US"},
    {"symbol": "NKE", "name": "NIKE, Inc.", "exchange": "NYSE", "market": "US"},

    # --- INDIAN INDICES (NSE & BSE) ---
    {"symbol": "^NSEI", "name": "NIFTY 50 Index", "exchange": "NSE", "market": "India"},
    {"symbol": "^BSESN", "name": "S&P BSE SENSEX", "exchange": "BSE", "market": "India"},
    {"symbol": "^NSEBANK", "name": "NIFTY BANK Index", "exchange": "NSE", "market": "India"},
    {"symbol": "^CNXIT", "name": "NIFTY IT Index", "exchange": "NSE", "market": "India"},

    # --- INDIAN NIFTY 50 & BLUECHIP LEADERS ---
    {"symbol": "RELIANCE.NS", "name": "Reliance Industries Limited", "exchange": "NSE", "market": "India"},
    {"symbol": "TCS.NS", "name": "Tata Consultancy Services Limited", "exchange": "NSE", "market": "India"},
    {"symbol": "HDFCBANK.NS", "name": "HDFC Bank Limited", "exchange": "NSE", "market": "India"},
    {"symbol": "INFY.NS", "name": "Infosys Limited", "exchange": "NSE", "market": "India"},
    {"symbol": "ICICIBANK.NS", "name": "ICICI Bank Limited", "exchange": "NSE", "market": "India"},
    {"symbol": "BHARTIARTL.NS", "name": "Bharti Airtel Limited", "exchange": "NSE", "market": "India"},
    {"symbol": "SBIN.NS", "name": "State Bank of India", "exchange": "NSE", "market": "India"},
    {"symbol": "LICI.NS", "name": "Life Insurance Corporation of India", "exchange": "NSE", "market": "India"},
    {"symbol": "ITC.NS", "name": "ITC Limited", "exchange": "NSE", "market": "India"},
    {"symbol": "HINDUNILVR.NS", "name": "Hindustan Unilever Limited", "exchange": "NSE", "market": "India"},
    {"symbol": "LT.NS", "name": "Larsen & Toubro Limited", "exchange": "NSE", "market": "India"},
    {"symbol": "BAJFINANCE.NS", "name": "Bajaj Finance Limited", "exchange": "NSE", "market": "India"},
    {"symbol": "HCLTECH.NS", "name": "HCL Technologies Limited", "exchange": "NSE", "market": "India"},
    {"symbol": "KOTAKBANK.NS", "name": "Kotak Mahindra Bank Limited", "exchange": "NSE", "market": "India"},
    {"symbol": "AXISBANK.NS", "name": "Axis Bank Limited", "exchange": "NSE", "market": "India"},
    {"symbol": "SUNPHARMA.NS", "name": "Sun Pharmaceutical Industries", "exchange": "NSE", "market": "India"},
    {"symbol": "TITAN.NS", "name": "Titan Company Limited", "exchange": "NSE", "market": "India"},
    {"symbol": "MARUTI.NS", "name": "Maruti Suzuki India Limited", "exchange": "NSE", "market": "India"},
    {"symbol": "TATASTEEL.NS", "name": "Tata Steel Limited", "exchange": "NSE", "market": "India"},
    {"symbol": "TATAPOWER.NS", "name": "Tata Power Company Limited", "exchange": "NSE", "market": "India"},
    {"symbol": "TATACOMM.NS", "name": "Tata Communications Limited", "exchange": "NSE", "market": "India"},
    {"symbol": "ULTRACEMCO.NS", "name": "UltraTech Cement Limited", "exchange": "NSE", "market": "India"},
    {"symbol": "BAJAJFINSV.NS", "name": "Bajaj Finserv Limited", "exchange": "NSE", "market": "India"},
    {"symbol": "BAJAJ-AUTO.NS", "name": "Bajaj Auto Limited", "exchange": "NSE", "market": "India"},
    {"symbol": "HEROMOTOCO.NS", "name": "Hero MotoCorp Limited", "exchange": "NSE", "market": "India"},
    {"symbol": "NTPC.NS", "name": "NTPC Limited", "exchange": "NSE", "market": "India"},
    {"symbol": "ONGC.NS", "name": "Oil and Natural Gas Corporation", "exchange": "NSE", "market": "India"},
    {"symbol": "POWERGRID.NS", "name": "Power Grid Corporation of India", "exchange": "NSE", "market": "India"},
    {"symbol": "ADANIENT.NS", "name": "Adani Enterprises Limited", "exchange": "NSE", "market": "India"},
    {"symbol": "ADANIPORTS.NS", "name": "Adani Ports and SEZ Limited", "exchange": "NSE", "market": "India"},
    {"symbol": "COALINDIA.NS", "name": "Coal India Limited", "exchange": "NSE", "market": "India"},
    {"symbol": "ASIANPAINT.NS", "name": "Asian Paints Limited", "exchange": "NSE", "market": "India"},
    {"symbol": "JSWSTEEL.NS", "name": "JSW Steel Limited", "exchange": "NSE", "market": "India"},
    {"symbol": "M&M.NS", "name": "Mahindra & Mahindra Limited", "exchange": "NSE", "market": "India"},
    {"symbol": "WIPRO.NS", "name": "Wipro Limited", "exchange": "NSE", "market": "India"},
    {"symbol": "GRASIM.NS", "name": "Grasim Industries Limited", "exchange": "NSE", "market": "India"},
    {"symbol": "NESTLEIND.NS", "name": "Nestle India Limited", "exchange": "NSE", "market": "India"},
    {"symbol": "TECHM.NS", "name": "Tech Mahindra Limited", "exchange": "NSE", "market": "India"},
    {"symbol": "HINDALCO.NS", "name": "Hindalco Industries Limited", "exchange": "NSE", "market": "India"},
    {"symbol": "CIPLA.NS", "name": "Cipla Limited", "exchange": "NSE", "market": "India"},
    {"symbol": "DRREDDY.NS", "name": "Dr. Reddy's Laboratories", "exchange": "NSE", "market": "India"},
    {"symbol": "EICHERMOT.NS", "name": "Eicher Motors Limited", "exchange": "NSE", "market": "India"},
    {"symbol": "BPCL.NS", "name": "Bharat Petroleum Corporation", "exchange": "NSE", "market": "India"},
    {"symbol": "DIVISLAB.NS", "name": "Divi's Laboratories Limited", "exchange": "NSE", "market": "India"},
    {"symbol": "SBILIFE.NS", "name": "SBI Life Insurance Company", "exchange": "NSE", "market": "India"},
    {"symbol": "HDFCLIFE.NS", "name": "HDFC Life Insurance Company", "exchange": "NSE", "market": "India"},
    {"symbol": "BRITANNIA.NS", "name": "Britannia Industries Limited", "exchange": "NSE", "market": "India"},
    {"symbol": "APOLLOHOSP.NS", "name": "Apollo Hospitals Enterprise", "exchange": "NSE", "market": "India"},
    {"symbol": "BEL.NS", "name": "Bharat Electronics Limited", "exchange": "NSE", "market": "India"},
    {"symbol": "HAL.NS", "name": "Hindustan Aeronautics Limited", "exchange": "NSE", "market": "India"},
    {"symbol": "TRENT.NS", "name": "Trent Limited", "exchange": "NSE", "market": "India"},
    {"symbol": "VBL.NS", "name": "Varun Beverages Limited", "exchange": "NSE", "market": "India"},
    {"symbol": "INDUSINDBK.NS", "name": "IndusInd Bank Limited", "exchange": "NSE", "market": "India"},
    {"symbol": "VEDL.NS", "name": "Vedanta Limited", "exchange": "NSE", "market": "India"},
    {"symbol": "JIOFIN.NS", "name": "Jio Financial Services Limited", "exchange": "NSE", "market": "India"},
]


def search_local_watchlist(query: str, limit: int = 8) -> List[Dict[str, str]]:
    """Instant substring matching on symbol and company name."""
    if not query:
        return CURATED_WATCHLIST[:limit]
    
    q = query.strip().upper()
    matches = []
    
    # Priority 1: exact symbol match
    for item in CURATED_WATCHLIST:
        if item["symbol"].upper() == q:
            matches.append(item)
            
    # Priority 2: symbol starts with query
    for item in CURATED_WATCHLIST:
        if item not in matches and item["symbol"].upper().startswith(q):
            matches.append(item)
            
    # Priority 3: name contains query
    for item in CURATED_WATCHLIST:
        if item not in matches and (q in item["name"].upper() or q in item["symbol"].upper()):
            matches.append(item)
            
    return matches[:limit]


def search_yahoo_online(query: str, limit: int = 8) -> List[Dict[str, str]]:
    """Fetches real-time ticker quotes and company names from Yahoo Finance."""
    if not query or len(query.strip()) < 1:
        return []
    
    url = f"https://query2.finance.yahoo.com/v1/finance/search?q={urllib.parse.quote(query)}&quotesCount={limit}&newsCount=0"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=3.5) as response:
            data = json.loads(response.read().decode("utf-8"))
            quotes = data.get("quotes", [])
            results = []
            for q in quotes:
                sym = q.get("symbol")
                if not sym:
                    continue
                name = q.get("shortname") or q.get("longname") or sym
                exchange = q.get("exchange", "")
                
                # Check market
                is_india = sym.endswith(".NS") or sym.endswith(".BO") or sym.startswith("^NSE") or sym.startswith("^BSE")
                market = "India" if is_india else "US / Global"
                
                results.append({
                    "symbol": sym,
                    "name": name,
                    "exchange": exchange,
                    "market": market
                })
            return results
    except Exception as e:
        # Graceful fallback: local search only if offline/network timeout
        return []


def search_stocks(query: str, limit: int = 10) -> List[Dict[str, str]]:
    """Combined search: local matches first for speed, then external Yahoo hits."""
    q = query.strip()
    if not q:
        return CURATED_WATCHLIST[:limit]
        
    local = search_local_watchlist(q, limit=limit)
    if len(local) >= 4:
        return local
        
    # Supplement with online Yahoo search
    online = search_yahoo_online(q, limit=limit)
    seen = {item["symbol"].upper() for item in local}
    for item in online:
        if item["symbol"].upper() not in seen:
            local.append(item)
            seen.add(item["symbol"].upper())
            if len(local) >= limit:
                break
                
    return local[:limit]
