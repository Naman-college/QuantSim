"""
Prakshat/preload_data.py - Parallel offline dataset downloader using yfinance & ThreadPoolExecutor.
Member: Prakshat (Finance API and Charts API Integration).

Pre-downloads and caches 100 top US & Indian assets to 'data/' so the app runs 100% offline.
"""

import os  # Filesystem path utilities
import sys  # Python path manipulation so script can run directly from terminal
import time  # Used to measure total batch download duration
from concurrent.futures import ThreadPoolExecutor, as_completed  # Concurrent thread pool for parallel API downloads
import pandas as pd  # DataFrame cleaning and CSV export
import yfinance as yf  # Yahoo Finance API client

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Resolve project root directory (StockBackTest/)
if ROOT_DIR not in sys.path:  # Ensure project root is importable when script is invoked directly
    sys.path.insert(0, ROOT_DIR)  # Prepend root directory to sys.path

DATA_DIR = os.path.join(ROOT_DIR, "data")  # Target folder where all CSV caches are stored
os.makedirs(DATA_DIR, exist_ok=True)  # Create 'data/' directory if missing

US_ASSETS = [  # Tuple list of 50 US equities and ETFs: (ticker, name, exchange, market)
    ("SPY", "SPDR S&P 500 ETF Trust", "NYSE Arca", "US"),  # S&P 500 ETF
    ("QQQ", "Invesco QQQ Trust (Nasdaq 100)", "NASDAQ", "US"),  # Nasdaq 100 ETF
    ("DIA", "SPDR Dow Jones Industrial Average ETF", "NYSE Arca", "US"),  # Dow Jones ETF
    ("IWM", "iShares Russell 2000 ETF", "NYSE Arca", "US"),  # Russell 2000 ETF
    ("VOO", "Vanguard S&P 500 ETF", "NYSE Arca", "US"),  # Vanguard S&P 500 ETF
    ("VTI", "Vanguard Total Stock Market ETF", "NYSE Arca", "US"),  # Vanguard Total Market ETF
    ("GLD", "SPDR Gold Shares", "NYSE Arca", "US"),  # Gold ETF
    ("TLT", "iShares 20+ Year Treasury Bond ETF", "NASDAQ", "US"),  # 20Y Treasury ETF
    ("XLF", "Financial Select Sector SPDR Fund", "NYSE Arca", "US"),  # Financial Sector ETF
    ("XLK", "Technology Select Sector SPDR Fund", "NYSE Arca", "US"),  # Tech Sector ETF
    ("SOXX", "iShares Semiconductor ETF", "NASDAQ", "US"),  # Semiconductor ETF
    ("SMH", "VanEck Semiconductor ETF", "NASDAQ", "US"),  # Semiconductor ETF
    ("AAPL", "Apple Inc.", "NASDAQ", "US"),  # Apple
    ("MSFT", "Microsoft Corporation", "NASDAQ", "US"),  # Microsoft
    ("NVDA", "NVIDIA Corporation", "NASDAQ", "US"),  # NVIDIA
    ("AMZN", "Amazon.com, Inc.", "NASDAQ", "US"),  # Amazon
    ("GOOGL", "Alphabet Inc. (Class A)", "NASDAQ", "US"),  # Alphabet Class A
    ("GOOG", "Alphabet Inc. (Class C)", "NASDAQ", "US"),  # Alphabet Class C
    ("META", "Meta Platforms, Inc.", "NASDAQ", "US"),  # Meta
    ("TSLA", "Tesla, Inc.", "NASDAQ", "US"),  # Tesla
    ("BRK-B", "Berkshire Hathaway Inc.", "NYSE", "US"),  # Berkshire Hathaway
    ("AVGO", "Broadcom Inc.", "NASDAQ", "US"),  # Broadcom
    ("JPM", "JPMorgan Chase & Co.", "NYSE", "US"),  # JPMorgan
    ("LLY", "Eli Lilly and Company", "NYSE", "US"),  # Eli Lilly
    ("V", "Visa Inc.", "NYSE", "US"),  # Visa
    ("UNH", "UnitedHealth Group Incorporated", "NYSE", "US"),  # UnitedHealth
    ("MA", "Mastercard Incorporated", "NYSE", "US"),  # Mastercard
    ("COST", "Costco Wholesale Corporation", "NASDAQ", "US"),  # Costco
    ("PG", "The Procter & Gamble Company", "NYSE", "US"),  # Procter & Gamble
    ("HD", "The Home Depot, Inc.", "NYSE", "US"),  # Home Depot
    ("NFLX", "Netflix, Inc.", "NASDAQ", "US"),  # Netflix
    ("JNJ", "Johnson & Johnson", "NYSE", "US"),  # Johnson & Johnson
    ("BAC", "Bank of America Corporation", "NYSE", "US"),  # Bank of America
    ("WMT", "Walmart Inc.", "NYSE", "US"),  # Walmart
    ("ABBV", "AbbVie Inc.", "NYSE", "US"),  # AbbVie
    ("CRM", "Salesforce, Inc.", "NYSE", "US"),  # Salesforce
    ("ORCL", "Oracle Corporation", "NYSE", "US"),  # Oracle
    ("AMD", "Advanced Micro Devices, Inc.", "NASDAQ", "US"),  # AMD
    ("CVX", "Chevron Corporation", "NYSE", "US"),  # Chevron
    ("XOM", "Exxon Mobil Corporation", "NYSE", "US"),  # Exxon Mobil
    ("KO", "The Coca-Cola Company", "NYSE", "US"),  # Coca-Cola
    ("PEP", "PepsiCo, Inc.", "NASDAQ", "US"),  # PepsiCo
    ("MRK", "Merck & Co., Inc.", "NYSE", "US"),  # Merck
    ("ADBE", "Adobe Inc.", "NASDAQ", "US"),  # Adobe
    ("QCOM", "QUALCOMM Incorporated", "NASDAQ", "US"),  # Qualcomm
    ("CSCO", "Cisco Systems, Inc.", "NASDAQ", "US"),  # Cisco
    ("INTC", "Intel Corporation", "NASDAQ", "US"),  # Intel
    ("DIS", "The Walt Disney Company", "NYSE", "US"),  # Disney
    ("VZ", "Verizon Communications Inc.", "NYSE", "US"),  # Verizon
    ("NKE", "NIKE, Inc.", "NYSE", "US"),  # Nike
]

INDIA_ASSETS = [  # Tuple list of 50 Indian NSE/BSE indices and stocks
    ("^NSEI", "NIFTY 50 Index", "NSE", "India"),  # Nifty 50 Index
    ("^BSESN", "S&P BSE SENSEX", "BSE", "India"),  # BSE Sensex Index
    ("^NSEBANK", "NIFTY Bank Index", "NSE", "India"),  # Nifty Bank Index
    ("^CNXIT", "NIFTY IT Index", "NSE", "India"),  # Nifty IT Index
    ("RELIANCE.NS", "Reliance Industries Limited", "NSE", "India"),  # Reliance
    ("TCS.NS", "Tata Consultancy Services Limited", "NSE", "India"),  # TCS
    ("HDFCBANK.NS", "HDFC Bank Limited", "NSE", "India"),  # HDFC Bank
    ("INFY.NS", "Infosys Limited", "NSE", "India"),  # Infosys
    ("ICICIBANK.NS", "ICICI Bank Limited", "NSE", "India"),  # ICICI Bank
    ("BHARTIARTL.NS", "Bharti Airtel Limited", "NSE", "India"),  # Bharti Airtel
    ("SBIN.NS", "State Bank of India", "NSE", "India"),  # SBI
    ("LICI.NS", "Life Insurance Corporation of India", "NSE", "India"),  # LIC
    ("ITC.NS", "ITC Limited", "NSE", "India"),  # ITC
    ("HINDUNILVR.NS", "Hindustan Unilever Limited", "NSE", "India"),  # HUL
    ("LT.NS", "Larsen & Toubro Limited", "NSE", "India"),  # L&T
    ("BAJFINANCE.NS", "Bajaj Finance Limited", "NSE", "India"),  # Bajaj Finance
    ("HCLTECH.NS", "HCL Technologies Limited", "NSE", "India"),  # HCL Tech
    ("KOTAKBANK.NS", "Kotak Mahindra Bank Limited", "NSE", "India"),  # Kotak Bank
    ("AXISBANK.NS", "Axis Bank Limited", "NSE", "India"),  # Axis Bank
    ("SUNPHARMA.NS", "Sun Pharmaceutical Industries Limited", "NSE", "India"),  # Sun Pharma
    ("TITAN.NS", "Titan Company Limited", "NSE", "India"),  # Titan
    ("MARUTI.NS", "Maruti Suzuki India Limited", "NSE", "India"),  # Maruti Suzuki
    ("TATAPOWER.NS", "Tata Power Company Limited", "NSE", "India"),  # Tata Power
    ("ULTRACEMCO.NS", "UltraTech Cement Limited", "NSE", "India"),  # UltraTech Cement
    ("BAJAJFINSV.NS", "Bajaj Finserv Limited", "NSE", "India"),  # Bajaj Finserv
    ("NTPC.NS", "NTPC Limited", "NSE", "India"),  # NTPC
    ("ONGC.NS", "Oil and Natural Gas Corporation Limited", "NSE", "India"),  # ONGC
    ("POWERGRID.NS", "Power Grid Corporation of India Limited", "NSE", "India"),  # Power Grid
    ("TATASTEEL.NS", "Tata Steel Limited", "NSE", "India"),  # Tata Steel
    ("ADANIENT.NS", "Adani Enterprises Limited", "NSE", "India"),  # Adani Enterprises
    ("ADANIPORTS.NS", "Adani Ports and Special Economic Zone Limited", "NSE", "India"),  # Adani Ports
    ("COALINDIA.NS", "Coal India Limited", "NSE", "India"),  # Coal India
    ("ASIANPAINT.NS", "Asian Paints Limited", "NSE", "India"),  # Asian Paints
    ("JSWSTEEL.NS", "JSW Steel Limited", "NSE", "India"),  # JSW Steel
    ("M&M.NS", "Mahindra & Mahindra Limited", "NSE", "India"),  # M&M
    ("WIPRO.NS", "Wipro Limited", "NSE", "India"),  # Wipro
    ("GRASIM.NS", "Grasim Industries Limited", "NSE", "India"),  # Grasim
    ("NESTLEIND.NS", "Nestle India Limited", "NSE", "India"),  # Nestle India
    ("TECHM.NS", "Tech Mahindra Limited", "NSE", "India"),  # Tech Mahindra
    ("HINDALCO.NS", "Hindalco Industries Limited", "NSE", "India"),  # Hindalco
    ("CIPLA.NS", "Cipla Limited", "NSE", "India"),  # Cipla
    ("DRREDDY.NS", "Dr. Reddy's Laboratories Limited", "NSE", "India"),  # Dr. Reddy's
    ("EICHERMOT.NS", "Eicher Motors Limited", "NSE", "India"),  # Eicher Motors
    ("BPCL.NS", "Bharat Petroleum Corporation Limited", "NSE", "India"),  # BPCL
    ("DIVISLAB.NS", "Divi's Laboratories Limited", "NSE", "India"),  # Divi's Labs
    ("SBILIFE.NS", "SBI Life Insurance Company Limited", "NSE", "India"),  # SBI Life
    ("HDFCLIFE.NS", "HDFC Life Insurance Company Limited", "NSE", "India"),  # HDFC Life
    ("BRITANNIA.NS", "Britannia Industries Limited", "NSE", "India"),  # Britannia
    ("APOLLOHOSP.NS", "Apollo Hospitals Enterprise Limited", "NSE", "India"),  # Apollo Hospitals
    ("JIOFIN.NS", "Jio Financial Services Limited", "NSE", "India"),  # Jio Financial
    ("BEL.NS", "Bharat Electronics Limited", "NSE", "India"),  # BEL
    ("HAL.NS", "Hindustan Aeronautics Limited", "NSE", "India"),  # HAL
    ("TRENT.NS", "Trent Limited", "NSE", "India"),  # Trent
    ("VBL.NS", "Varun Beverages Limited", "NSE", "India"),  # Varun Beverages
]

ALL_PRELOAD_ASSETS = US_ASSETS + INDIA_ASSETS  # Combined list of all assets to pre-cache


def download_and_cache(ticker: str, start_date: str = "2020-01-01") -> bool:
    """Downloads one ticker from Yahoo Finance, cleans its DataFrame, and writes a CSV cache file."""
    safe_ticker = ticker.replace("^", "").replace(".", "_")  # Sanitize ticker into safe filename
    cache_path = os.path.join(DATA_DIR, f"{safe_ticker}.csv")  # Destination CSV file path

    try:
        raw_df = yf.download(ticker, start=start_date, progress=False, auto_adjust=True)  # Download adjusted OHLCV history
        if raw_df is None or raw_df.empty:  # Abort if Yahoo returned no rows
            print(f"  [WARN] No data returned for {ticker}")  # Print warning
            return False  # Signal failure for this asset

        if isinstance(raw_df.columns, pd.MultiIndex):  # Flatten MultiIndex columns if present
            for lvl in range(raw_df.columns.nlevels):  # Search levels for 'Close'
                vals = raw_df.columns.get_level_values(lvl)  # Extract level labels
                if 'Close' in vals:  # Found OHLCV header level
                    raw_df.columns = vals  # Assign single-level columns
                    break  # Stop searching levels
            else:
                raw_df.columns = raw_df.columns.get_level_values(0)  # Fallback to first level

        if 'Close' not in raw_df.columns and 'Adj Close' in raw_df.columns:  # Ensure 'Close' exists
            raw_df['Close'] = raw_df['Adj Close']  # Alias 'Adj Close'

        if hasattr(raw_df.index, 'tz') and raw_df.index.tz is not None:  # Strip timezone if attached
            raw_df.index = raw_df.index.tz_localize(None)  # Make index tz-naive
        else:
            raw_df.index = pd.to_datetime(raw_df.index)  # Cast index to DateTimeIndex

        raw_df = raw_df.ffill().bfill().dropna()  # Fill missing trading gaps cleanly
        if len(raw_df) < 5:  # Require at least 5 bars to be useful
            return False  # Skip tiny/invalid datasets

        raw_df.to_csv(cache_path)  # Save CSV to disk
        return True  # Signal success
    except Exception as e:
        print(f"  [FAIL] {ticker}: {e}")  # Print failure reason
        return False  # Signal failure


def main():
    """Runs parallel download workers to populate the offline CSV cache."""
    print("=" * 70)  # Print header banner
    print("QUANTSIM OFFLINE PACK: PRE-DOWNLOADING TOP US & INDIAN ASSETS")  # Print task title
    print(f"Target Directory: {DATA_DIR}")  # Show output directory
    print(f"Total Assets to Cache: {len(ALL_PRELOAD_ASSETS)}")  # Show total asset count
    print("=" * 70)  # Print divider

    start_time = time.time()  # Record start timestamp for elapsed time reporting
    success_count = 0  # Counter for successful downloads
    fail_count = 0  # Counter for failed downloads

    with ThreadPoolExecutor(max_workers=8) as executor:  # Spawn up to 8 concurrent download threads
        future_map = {  # Map each Future object back to its ticker symbol
            executor.submit(download_and_cache, item[0]): item[0]  # Submit download task to thread pool
            for item in ALL_PRELOAD_ASSETS  # Iterate through all US and Indian assets
        }

        for idx, future in enumerate(as_completed(future_map), 1):  # Process futures as soon as each finishes
            sym = future_map[future]  # Retrieve ticker symbol for this future
            try:
                ok = future.result()  # Unwrap boolean return value from worker thread
                if ok:  # Increment success or fail counter and log status
                    success_count += 1  # Track cached file
                    print(f"[{idx:03d}/{len(ALL_PRELOAD_ASSETS)}] Cached: {sym:<15} [OK]")  # Print OK line
                else:
                    fail_count += 1  # Track failure
                    print(f"[{idx:03d}/{len(ALL_PRELOAD_ASSETS)}] Failed: {sym:<15} [ERR]")  # Print ERR line
            except Exception as e:
                fail_count += 1  # Track exception as failure
                print(f"[{idx:03d}/{len(ALL_PRELOAD_ASSETS)}] Error:  {sym:<15} {e}")  # Print exception details

    elapsed = time.time() - start_time  # Compute total runtime in seconds
    print("\n" + "=" * 70)  # Print footer banner
    print(f"PRELOAD COMPLETED in {elapsed:.1f}s!")  # Print elapsed duration
    print(f"Successfully Cached: {success_count} / {len(ALL_PRELOAD_ASSETS)} assets")  # Summary count
    print(f"Failed: {fail_count}")  # Failure count
    print(f"All files saved to: {DATA_DIR}")  # Cache folder path
    print("QuantSim can now run 100% OFFLINE during presentations!")  # Confirmation message
    print("=" * 70)  # Closing divider


if __name__ == "__main__":  # Run main() only when executed directly as a script
    main()  # Invoke parallel preloader
