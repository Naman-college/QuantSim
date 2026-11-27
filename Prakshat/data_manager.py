"""
Prakshat/data_manager.py - Historical market data ingestion (Yahoo Finance API) & local CSV caching.
Member: Prakshat (Finance API and Charts API Integration).

Key Concepts:
- Fetching adjusted OHLCV time series via yfinance
- Local CSV disk caching for fast offline backtesting
- Timezone normalization and missing-value cleaning (ffill / bfill / dropna)
"""

import os  # Standard library module for filesystem paths and directory creation
import pandas as pd  # Data analysis library used for DataFrames and date slicing
import yfinance as yf  # Unofficial Yahoo Finance API wrapper for downloading stock data

# Compute the root 'data/' directory path relative to this file (StockBackTest/data)
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
os.makedirs(CACHE_DIR, exist_ok=True)  # Create the cache folder automatically if it does not exist


def fetch_stock_data(ticker: str, start_date: str = "2020-01-01", end_date: str = None, use_cache: bool = True) -> pd.DataFrame:
    """
    Downloads historical daily stock data from Yahoo Finance and caches it locally as CSV.

    Parameters:
        ticker (str): Stock/ETF symbol (e.g. 'AAPL', 'SPY', 'RELIANCE.NS')
        start_date (str): Beginning date in 'YYYY-MM-DD' format
        end_date (str): End date in 'YYYY-MM-DD' format (default: today)
        use_cache (bool): If True, checks local disk cache first before hitting Yahoo Finance API

    Returns:
        pd.DataFrame: Cleaned DataFrame with DatetimeIndex and ['Open', 'High', 'Low', 'Close', 'Volume']
    """
    safe_ticker = ticker.replace("^", "").replace(".", "_")  # Sanitize special ticker chars ('^', '.') for valid Windows/Linux filenames
    cache_path = os.path.join(CACHE_DIR, f"{safe_ticker}.csv")  # Full path to the cached CSV file for this ticker

    requested_start = pd.to_datetime(start_date).tz_localize(None)  # Parse start_date into a timezone-naive pandas Timestamp
    requested_end = pd.to_datetime(end_date).tz_localize(None) if end_date else None  # Parse optional end_date or leave as None

    cached_df_available = None  # Holds any valid cached DataFrame as an offline fallback
    if os.path.exists(cache_path):  # Check if a local CSV cache already exists on disk
        try:
            cached_df = pd.read_csv(cache_path, index_col=0, parse_dates=True)  # Load CSV with column 0 parsed as DatetimeIndex
            if hasattr(cached_df.index, 'tz') and cached_df.index.tz is not None:  # Check if index carries timezone info
                cached_df.index = cached_df.index.tz_localize(None)  # Strip timezone so date comparisons never raise TypeError
            else:
                cached_df.index = pd.to_datetime(cached_df.index)  # Ensure index is strictly DateTime64 dtype

            cached_df_available = cached_df  # Save parsed cache for potential offline fallback below

            if use_cache and not cached_df.empty:  # Only serve directly from cache if caching is enabled and non-empty
                cache_start = cached_df.index.min()  # Earliest trading date stored in the local cache
                if cache_start <= requested_start + pd.Timedelta(days=7):  # Allow up to 7-day buffer for weekends/market holidays
                    filtered_df = cached_df.loc[cached_df.index >= requested_start]  # Slice rows on or after requested_start
                    if requested_end:  # If an upper date bound was provided
                        filtered_df = filtered_df.loc[filtered_df.index <= requested_end]  # Slice rows on or before requested_end
                    if not filtered_df.empty and len(filtered_df) >= 5:  # Ensure at least 5 trading days exist for valid metrics
                        return filtered_df  # Fast-path return from disk cache without network call
        except Exception as e:
            print(f"Cache read error for {ticker}: {e}.")  # Log corrupted/unreadable cache and fall through to API download

    print(f"Downloading historical data for {ticker} from Yahoo Finance...")  # Console log indicating live Finance API call
    try:
        raw_df = yf.download(ticker, start=start_date, end=end_date, progress=False, auto_adjust=True)  # Fetch dividend/split-adjusted OHLCV bars
    except Exception as e:
        print(f"Yahoo Finance download failed: {e}")  # Catch network timeouts or API errors gracefully
        raw_df = None  # Mark download as failed so offline fallback logic can run

    if raw_df is None or raw_df.empty:  # If online API returned nothing or failed
        if cached_df_available is not None and not cached_df_available.empty:  # Check if we still have a local CSV backup
            print(f"Using cached data fallback for {ticker} (offline mode).")  # Inform user we are running offline
            filtered_df = cached_df_available.loc[cached_df_available.index >= requested_start]  # Filter backup cache from start date
            if not filtered_df.empty and len(filtered_df) >= 5:  # Return sliced cache if enough rows exist
                return filtered_df
            return cached_df_available  # Otherwise return full cached history
        raise ValueError(f"No price data found for ticker '{ticker}'. Please check the symbol or internet connection.")  # Fail clearly if neither API nor cache has data

    if isinstance(raw_df.columns, pd.MultiIndex):  # Newer yfinance versions return MultiIndex columns like ('Close', 'SPY')
        matched = False  # Flag tracking whether we found the price level containing 'Close'
        for lvl in range(raw_df.columns.nlevels):  # Inspect each level of the MultiIndex
            vals = raw_df.columns.get_level_values(lvl)  # Extract column names at this level
            if 'Close' in vals:  # Check if this level holds OHLCV names
                raw_df.columns = vals  # Flatten columns to single-level names ('Open', 'High', 'Low', 'Close', 'Volume')
                matched = True  # Record success
                break  # Stop scanning levels
        if not matched:  # Fallback if 'Close' wasn't found at any level
            raw_df.columns = raw_df.columns.get_level_values(0)  # Flatten using top level

    if 'Close' not in raw_df.columns:  # Verify a 'Close' price column exists for strategy math
        if 'Adj Close' in raw_df.columns:  # Some datasets only expose 'Adj Close'
            raw_df['Close'] = raw_df['Adj Close']  # Alias 'Adj Close' to 'Close'
        else:
            raise ValueError(f"Missing 'Close' column for ticker '{ticker}'. Available columns: {list(raw_df.columns)}")  # Cannot backtest without closing prices

    if hasattr(raw_df.index, 'tz') and raw_df.index.tz is not None:  # Check if Yahoo returned timezone-aware timestamps
        raw_df.index = raw_df.index.tz_localize(None)  # Normalize index to timezone-naive timestamps
    else:
        raw_df.index = pd.to_datetime(raw_df.index)  # Guarantee index is DatetimeIndex

    raw_df = raw_df.ffill().bfill().dropna()  # Forward-fill then back-fill missing trading gaps, dropping any remaining NaNs

    try:
        raw_df.to_csv(cache_path)  # Persist cleaned DataFrame to local CSV cache for future offline runs
    except Exception as e:
        print(f"Cache write error: {e}")  # Non-fatal if disk write fails (e.g. read-only permissions)

    final_df = raw_df.loc[raw_df.index >= requested_start]  # Filter result to requested start date
    if requested_end:  # Apply optional end-date filter
        final_df = final_df.loc[final_df.index <= requested_end]  # Slice up to requested_end
    return final_df if not final_df.empty else raw_df  # Return sliced DataFrame (or full raw_df if slice was empty)
