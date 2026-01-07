"""
Alternative stock data fetcher using Alpha Vantage API (free tier)
"""
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time


class AlphaVantageStockFetcher:
    """Fetches stock data using Alpha Vantage API (free alternative to yfinance)"""

    def __init__(self, api_key: str = "demo"):
        """
        Initialize with Alpha Vantage API key
        Get free key at: https://www.alphavantage.co/support/#api-key
        """
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"
        self.cache = {}
        self.cache_timeout = timedelta(minutes=15)

    def get_stock_data(self, symbol: str, retries: int = 3) -> Optional[pd.DataFrame]:
        """
        Fetch stock data for a given symbol

        Args:
            symbol: Stock ticker symbol
            retries: Number of retry attempts

        Returns:
            DataFrame with stock data or None if fetch fails
        """
        # Check cache first
        cache_key = f"{symbol}_daily"
        if cache_key in self.cache:
            cached_time, cached_data = self.cache[cache_key]
            if datetime.now() - cached_time < self.cache_timeout:
                print(f"Using cached data for {symbol}")
                return cached_data

        for attempt in range(retries):
            try:
                print(f"Fetching {symbol} from Alpha Vantage (attempt {attempt + 1}/{retries})...")

                params = {
                    'function': 'TIME_SERIES_DAILY',
                    'symbol': symbol,
                    'apikey': self.api_key,
                    'outputsize': 'compact'  # Last 100 days
                }

                response = requests.get(self.base_url, params=params, timeout=10)
                data = response.json()

                # Check for errors
                if 'Error Message' in data:
                    print(f"API Error for {symbol}: {data['Error Message']}")
                    return None

                if 'Note' in data:
                    print(f"API Rate Limit: {data['Note']}")
                    if attempt < retries - 1:
                        time.sleep(15)  # Wait before retry
                        continue
                    return None

                if 'Time Series (Daily)' not in data:
                    print(f"No data in response for {symbol}")
                    if attempt < retries - 1:
                        time.sleep(2)
                        continue
                    return None

                # Convert to pandas DataFrame
                time_series = data['Time Series (Daily)']
                df = pd.DataFrame.from_dict(time_series, orient='index')

                # Rename columns to match yfinance format
                df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
                df.index = pd.to_datetime(df.index)
                df = df.sort_index()

                # Convert to numeric
                for col in df.columns:
                    df[col] = pd.to_numeric(df[col])

                # Cache the data
                self.cache[cache_key] = (datetime.now(), df)

                print(f"Successfully fetched {len(df)} rows for {symbol}")
                return df

            except Exception as e:
                print(f"Error fetching {symbol} (attempt {attempt + 1}): {e}")
                if attempt < retries - 1:
                    time.sleep(2)
                else:
                    import traceback
                    traceback.print_exc()
                    return None

        return None

    def get_multiple_stocks(self, symbols: List[str]) -> Dict[str, pd.DataFrame]:
        """
        Fetch data for multiple stocks with rate limiting

        Args:
            symbols: List of stock ticker symbols

        Returns:
            Dictionary mapping symbols to their DataFrames
        """
        results = {}

        for i, symbol in enumerate(symbols):
            data = self.get_stock_data(symbol)
            if data is not None:
                results[symbol] = data

            # Rate limiting: 5 calls per minute for free tier
            if i < len(symbols) - 1:  # Don't wait after last stock
                print(f"Waiting 12 seconds (API rate limit)...")
                time.sleep(12)

        return results
