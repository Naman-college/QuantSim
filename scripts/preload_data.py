"""
preload_data.py - Pre-download and cache top 50 US and top 50 Indian stocks/indexes.
Ensures 100% offline capability for classroom presentations and vivas.
"""

import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
import yfinance as yf

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

DATA_DIR = os.path.join(ROOT_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

US_ASSETS = [
    # US Major Indices & Key Sector ETFs
    ("SPY", "SPDR S&P 500 ETF Trust", "NYSE Arca", "US"),
    ("QQQ", "Invesco QQQ Trust (Nasdaq 100)", "NASDAQ", "US"),
    ("DIA", "SPDR Dow Jones Industrial Average ETF", "NYSE Arca", "US"),
    ("IWM", "iShares Russell 2000 ETF", "NYSE Arca", "US"),
    ("VOO", "Vanguard S&P 500 ETF", "NYSE Arca", "US"),
    ("VTI", "Vanguard Total Stock Market ETF", "NYSE Arca", "US"),
    ("GLD", "SPDR Gold Shares", "NYSE Arca", "US"),
    ("TLT", "iShares 20+ Year Treasury Bond ETF", "NASDAQ", "US"),
    ("XLF", "Financial Select Sector SPDR Fund", "NYSE Arca", "US"),
    ("XLK", "Technology Select Sector SPDR Fund", "NYSE Arca", "US"),
    ("SOXX", "iShares Semiconductor ETF", "NASDAQ", "US"),
    ("SMH", "VanEck Semiconductor ETF", "NASDAQ", "US"),
    # US Mega-Cap & Bluechip Leaders
    ("AAPL", "Apple Inc.", "NASDAQ", "US"),
    ("MSFT", "Microsoft Corporation", "NASDAQ", "US"),
    ("NVDA", "NVIDIA Corporation", "NASDAQ", "US"),
    ("AMZN", "Amazon.com, Inc.", "NASDAQ", "US"),
    ("GOOGL", "Alphabet Inc. (Class A)", "NASDAQ", "US"),
    ("GOOG", "Alphabet Inc. (Class C)", "NASDAQ", "US"),
    ("META", "Meta Platforms, Inc.", "NASDAQ", "US"),
    ("TSLA", "Tesla, Inc.", "NASDAQ", "US"),
    ("BRK-B", "Berkshire Hathaway Inc.", "NYSE", "US"),
    ("AVGO", "Broadcom Inc.", "NASDAQ", "US"),
    ("JPM", "JPMorgan Chase & Co.", "NYSE", "US"),
    ("LLY", "Eli Lilly and Company", "NYSE", "US"),
    ("V", "Visa Inc.", "NYSE", "US"),
    ("UNH", "UnitedHealth Group Incorporated", "NYSE", "US"),
    ("MA", "Mastercard Incorporated", "NYSE", "US"),
    ("COST", "Costco Wholesale Corporation", "NASDAQ", "US"),
    ("PG", "The Procter & Gamble Company", "NYSE", "US"),
    ("HD", "The Home Depot, Inc.", "NYSE", "US"),
    ("NFLX", "Netflix, Inc.", "NASDAQ", "US"),
    ("JNJ", "Johnson & Johnson", "NYSE", "US"),
    ("BAC", "Bank of America Corporation", "NYSE", "US"),
    ("WMT", "Walmart Inc.", "NYSE", "US"),
    ("ABBV", "AbbVie Inc.", "NYSE", "US"),
    ("CRM", "Salesforce, Inc.", "NYSE", "US"),
    ("ORCL", "Oracle Corporation", "NYSE", "US"),
    ("AMD", "Advanced Micro Devices, Inc.", "NASDAQ", "US"),
    ("CVX", "Chevron Corporation", "NYSE", "US"),
    ("XOM", "Exxon Mobil Corporation", "NYSE", "US"),
    ("KO", "The Coca-Cola Company", "NYSE", "US"),
    ("PEP", "PepsiCo, Inc.", "NASDAQ", "US"),
    ("MRK", "Merck & Co., Inc.", "NYSE", "US"),
    ("ADBE", "Adobe Inc.", "NASDAQ", "US"),
    ("QCOM", "QUALCOMM Incorporated", "NASDAQ", "US"),
    ("CSCO", "Cisco Systems, Inc.", "NASDAQ", "US"),
    ("INTC", "Intel Corporation", "NASDAQ", "US"),
    ("DIS", "The Walt Disney Company", "NYSE", "US"),
    ("VZ", "Verizon Communications Inc.", "NYSE", "US"),
    ("NKE", "NIKE, Inc.", "NYSE", "US"),
]

INDIA_ASSETS = [
    # Indian Indices
    ("^NSEI", "NIFTY 50 Index", "NSE", "India"),
    ("^BSESN", "S&P BSE SENSEX", "BSE", "India"),
    ("^NSEBANK", "NIFTY Bank Index", "NSE", "India"),
    ("^CNXIT", "NIFTY IT Index", "NSE", "India"),
    # Top Nifty 50 Bluechips
    ("RELIANCE.NS", "Reliance Industries Limited", "NSE", "India"),
    ("TCS.NS", "Tata Consultancy Services Limited", "NSE", "India"),
    ("HDFCBANK.NS", "HDFC Bank Limited", "NSE", "India"),
    ("INFY.NS", "Infosys Limited", "NSE", "India"),
    ("ICICIBANK.NS", "ICICI Bank Limited", "NSE", "India"),
    ("BHARTIARTL.NS", "Bharti Airtel Limited", "NSE", "India"),
    ("SBIN.NS", "State Bank of India", "NSE", "India"),
    ("LICI.NS", "Life Insurance Corporation of India", "NSE", "India"),
    ("ITC.NS", "ITC Limited", "NSE", "India"),
    ("HINDUNILVR.NS", "Hindustan Unilever Limited", "NSE", "India"),
    ("LT.NS", "Larsen & Toubro Limited", "NSE", "India"),
    ("BAJFINANCE.NS", "Bajaj Finance Limited", "NSE", "India"),
    ("HCLTECH.NS", "HCL Technologies Limited", "NSE", "India"),
    ("KOTAKBANK.NS", "Kotak Mahindra Bank Limited", "NSE", "India"),
    ("AXISBANK.NS", "Axis Bank Limited", "NSE", "India"),
    ("SUNPHARMA.NS", "Sun Pharmaceutical Industries Limited", "NSE", "India"),
    ("TITAN.NS", "Titan Company Limited", "NSE", "India"),
    ("MARUTI.NS", "Maruti Suzuki India Limited", "NSE", "India"),
    ("TATAPOWER.NS", "Tata Power Company Limited", "NSE", "India"),
    ("ULTRACEMCO.NS", "UltraTech Cement Limited", "NSE", "India"),
    ("BAJAJFINSV.NS", "Bajaj Finserv Limited", "NSE", "India"),
    ("NTPC.NS", "NTPC Limited", "NSE", "India"),
    ("ONGC.NS", "Oil and Natural Gas Corporation Limited", "NSE", "India"),
    ("POWERGRID.NS", "Power Grid Corporation of India Limited", "NSE", "India"),
    ("TATASTEEL.NS", "Tata Steel Limited", "NSE", "India"),
    ("ADANIENT.NS", "Adani Enterprises Limited", "NSE", "India"),
    ("ADANIPORTS.NS", "Adani Ports and Special Economic Zone Limited", "NSE", "India"),
    ("COALINDIA.NS", "Coal India Limited", "NSE", "India"),
    ("ASIANPAINT.NS", "Asian Paints Limited", "NSE", "India"),
    ("JSWSTEEL.NS", "JSW Steel Limited", "NSE", "India"),
    ("M&M.NS", "Mahindra & Mahindra Limited", "NSE", "India"),
    ("WIPRO.NS", "Wipro Limited", "NSE", "India"),
    ("GRASIM.NS", "Grasim Industries Limited", "NSE", "India"),
    ("NESTLEIND.NS", "Nestle India Limited", "NSE", "India"),
    ("TECHM.NS", "Tech Mahindra Limited", "NSE", "India"),
    ("HINDALCO.NS", "Hindalco Industries Limited", "NSE", "India"),
    ("CIPLA.NS", "Cipla Limited", "NSE", "India"),
    ("DRREDDY.NS", "Dr. Reddy's Laboratories Limited", "NSE", "India"),
    ("EICHERMOT.NS", "Eicher Motors Limited", "NSE", "India"),
    ("BPCL.NS", "Bharat Petroleum Corporation Limited", "NSE", "India"),
    ("DIVISLAB.NS", "Divi's Laboratories Limited", "NSE", "India"),
    ("SBILIFE.NS", "SBI Life Insurance Company Limited", "NSE", "India"),
    ("HDFCLIFE.NS", "HDFC Life Insurance Company Limited", "NSE", "India"),
    ("BRITANNIA.NS", "Britannia Industries Limited", "NSE", "India"),
    ("APOLLOHOSP.NS", "Apollo Hospitals Enterprise Limited", "NSE", "India"),
    ("JIOFIN.NS", "Jio Financial Services Limited", "NSE", "India"),
    ("BEL.NS", "Bharat Electronics Limited", "NSE", "India"),
    ("HAL.NS", "Hindustan Aeronautics Limited", "NSE", "India"),
    ("TRENT.NS", "Trent Limited", "NSE", "India"),
    ("VBL.NS", "Varun Beverages Limited", "NSE", "India"),
]

ALL_PRELOAD_ASSETS = US_ASSETS + INDIA_ASSETS


def download_and_cache(ticker: str, start_date: str = "2020-01-01") -> bool:
    safe_ticker = ticker.replace("^", "").replace(".", "_")
    cache_path = os.path.join(DATA_DIR, f"{safe_ticker}.csv")

    try:
        raw_df = yf.download(ticker, start=start_date, progress=False, auto_adjust=True)
        if raw_df is None or raw_df.empty:
            print(f"  [WARN] No data returned for {ticker}")
            return False

        # Flatten MultiIndex if returned
        if isinstance(raw_df.columns, pd.MultiIndex):
            for lvl in range(raw_df.columns.nlevels):
                vals = raw_df.columns.get_level_values(lvl)
                if 'Close' in vals:
                    raw_df.columns = vals
                    break
            else:
                raw_df.columns = raw_df.columns.get_level_values(0)

        if 'Close' not in raw_df.columns and 'Adj Close' in raw_df.columns:
            raw_df['Close'] = raw_df['Adj Close']

        # Clean index and gaps
        if hasattr(raw_df.index, 'tz') and raw_df.index.tz is not None:
            raw_df.index = raw_df.index.tz_localize(None)
        else:
            raw_df.index = pd.to_datetime(raw_df.index)

        raw_df = raw_df.ffill().bfill().dropna()
        if len(raw_df) < 5:
            return False

        raw_df.to_csv(cache_path)
        return True
    except Exception as e:
        print(f"  [FAIL] {ticker}: {e}")
        return False


def main():
    print("=" * 70)
    print("QUANTSIM OFFLINE PACK: PRE-DOWNLOADING 100 TOP US & INDIAN ASSETS")
    print(f"Target Directory: {DATA_DIR}")
    print(f"Total Assets to Cache: {len(ALL_PRELOAD_ASSETS)} (50 US + 50 India)")
    print("=" * 70)

    start_time = time.time()
    success_count = 0
    fail_count = 0

    # Download with 8 concurrent worker threads
    with ThreadPoolExecutor(max_workers=8) as executor:
        future_map = {
            executor.submit(download_and_cache, item[0]): item[0]
            for item in ALL_PRELOAD_ASSETS
        }

        for idx, future in enumerate(as_completed(future_map), 1):
            sym = future_map[future]
            try:
                ok = future.result()
                if ok:
                    success_count += 1
                    print(f"[{idx:03d}/100] Cached: {sym:<15} [OK]")
                else:
                    fail_count += 1
                    print(f"[{idx:03d}/100] Failed: {sym:<15} [ERR]")
            except Exception as e:
                fail_count += 1
                print(f"[{idx:03d}/100] Error:  {sym:<15} {e}")

    elapsed = time.time() - start_time
    print("\n" + "=" * 70)
    print(f"PRELOAD COMPLETED in {elapsed:.1f}s!")
    print(f"Successfully Cached: {success_count} / {len(ALL_PRELOAD_ASSETS)} assets")
    print(f"Failed: {fail_count}")
    print(f"All files saved to: {DATA_DIR}")
    print("QuantSim can now run 100% OFFLINE during presentations!")
    print("=" * 70)


if __name__ == "__main__":
    main()
