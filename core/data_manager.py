"""
data_manager.py - Data ingestion and caching module using yfinance and pandas.
Maintained by Member 1 (Data Engineer).

Academic Concepts Showcased:
- pandas DataFrame creation and DatetimeIndex manipulation
- Handling missing data with ffill() and dropna()
- File caching with CSV/Parquet for high performance
"""

import os
import pandas as pd
import yfinance as yf

CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
os.makedirs(CACHE_DIR, exist_ok=True)


def fetch_stock_data(ticker: str, start_date: str = "2020-01-01", end_date: str = None, use_cache: bool = True) -> pd.DataFrame:
    """
    Downloads historical daily stock data from Yahoo Finance and caches it locally.
    
    Parameters:
        ticker (str): Stock/ETF symbol (e.g. 'AAPL', 'SPY', 'RELIANCE.NS')
        start_date (str): Beginning date in 'YYYY-MM-DD' format
        end_date (str): End date in 'YYYY-MM-DD' format (default: today)
        use_cache (bool): If True, checks local disk cache first before downloading
        
    Returns:
        pd.DataFrame: Cleaned DataFrame with DatetimeIndex and ['Open', 'High', 'Low', 'Close', 'Volume']
    """
    # Clean ticker string for filesystem safety (e.g. '^NSEI' -> 'NSEI')
    safe_ticker = ticker.replace("^", "").replace(".", "_")
    cache_path = os.path.join(CACHE_DIR, f"{safe_ticker}.csv")

    df = None
    requested_start = pd.to_datetime(start_date).tz_localize(None)
    requested_end = pd.to_datetime(end_date).tz_localize(None) if end_date else None

    # Step 1: Check if cached file exists and covers the requested timeframe
    cached_df_available = None
    if os.path.exists(cache_path):
        try:
            cached_df = pd.read_csv(cache_path, index_col=0, parse_dates=True)
            if hasattr(cached_df.index, 'tz') and cached_df.index.tz is not None:
                cached_df.index = cached_df.index.tz_localize(None)
            else:
                cached_df.index = pd.to_datetime(cached_df.index)

            cached_df_available = cached_df

            # Check if cache covers requested start date (within 7 calendar days for weekends/holidays)
            if use_cache and not cached_df.empty:
                cache_start = cached_df.index.min()
                if cache_start <= requested_start + pd.Timedelta(days=7):
                    filtered_df = cached_df.loc[cached_df.index >= requested_start]
                    if requested_end:
                        filtered_df = filtered_df.loc[filtered_df.index <= requested_end]
                    if not filtered_df.empty and len(filtered_df) >= 5:
                        return filtered_df
        except Exception as e:
            print(f"Cache read error for {ticker}: {e}.")

    # Step 2: Download fresh data from Yahoo Finance
    print(f"Downloading historical data for {ticker} from Yahoo Finance...")
    try:
        raw_df = yf.download(ticker, start=start_date, end=end_date, progress=False, auto_adjust=True)
    except Exception as e:
        print(f"Yahoo Finance download failed: {e}")
        raw_df = None

    if raw_df is None or raw_df.empty:
        # Fallback to whatever cache we had if download failed (e.g. offline mode)
        if cached_df_available is not None and not cached_df_available.empty:
            print(f"Using cached data fallback for {ticker} (offline mode).")
            filtered_df = cached_df_available.loc[cached_df_available.index >= requested_start]
            if not filtered_df.empty and len(filtered_df) >= 5:
                return filtered_df
            return cached_df_available
        raise ValueError(f"No price data found for ticker '{ticker}'. Please check the symbol or internet connection.")

    # Flatten MultiIndex columns if returned by newer yfinance versions
    if isinstance(raw_df.columns, pd.MultiIndex):
        matched = False
        for lvl in range(raw_df.columns.nlevels):
            vals = raw_df.columns.get_level_values(lvl)
            if 'Close' in vals:
                raw_df.columns = vals
                matched = True
                break
        if not matched:
            raw_df.columns = raw_df.columns.get_level_values(0)

    # Ensure 'Close' exists
    if 'Close' not in raw_df.columns:
        if 'Adj Close' in raw_df.columns:
            raw_df['Close'] = raw_df['Adj Close']
        else:
            raise ValueError(f"Missing 'Close' column for ticker '{ticker}'. Available columns: {list(raw_df.columns)}")

    # Step 3: Data Cleaning (Pandas Operations)
    # - Ensure index is tz-naive datetime
    if hasattr(raw_df.index, 'tz') and raw_df.index.tz is not None:
        raw_df.index = raw_df.index.tz_localize(None)
    else:
        raw_df.index = pd.to_datetime(raw_df.index)

    # - Handle any gaps or NaN values
    raw_df = raw_df.ffill().bfill().dropna()

    # Step 4: Save to local CSV cache
    try:
        raw_df.to_csv(cache_path)
    except Exception as e:
        print(f"Cache write error: {e}")

    # Return filtered to requested start_date
    final_df = raw_df.loc[raw_df.index >= requested_start]
    if requested_end:
        final_df = final_df.loc[final_df.index <= requested_end]
    return final_df if not final_df.empty else raw_df

