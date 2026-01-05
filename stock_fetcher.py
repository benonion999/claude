"""
Stock data fetcher module using yfinance API
"""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional


class StockDataFetcher:
    """Fetches stock data using yfinance API"""

    def __init__(self):
        self.cache = {}
        self.cache_timeout = timedelta(minutes=5)

    def get_stock_data(self, symbol: str, period: str = "1mo", interval: str = "1d") -> Optional[pd.DataFrame]:
        """
        Fetch stock data for a given symbol

        Args:
            symbol: Stock ticker symbol (e.g., 'ASML')
            period: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)

        Returns:
            DataFrame with stock data or None if fetch fails
        """
        try:
            stock = yf.Ticker(symbol)
            data = stock.history(period=period, interval=interval)

            if data.empty:
                print(f"Warning: No data returned for {symbol}")
                return None

            return data
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return None

    def get_current_price(self, symbol: str) -> Optional[float]:
        """
        Get current stock price

        Args:
            symbol: Stock ticker symbol

        Returns:
            Current price or None if fetch fails
        """
        cache_key = f"{symbol}_current"

        # Check cache
        if cache_key in self.cache:
            cached_time, cached_price = self.cache[cache_key]
            if datetime.now() - cached_time < self.cache_timeout:
                return cached_price

        try:
            stock = yf.Ticker(symbol)
            data = stock.history(period="1d", interval="1m")

            if not data.empty:
                current_price = data['Close'].iloc[-1]
                self.cache[cache_key] = (datetime.now(), current_price)
                return current_price

            return None
        except Exception as e:
            print(f"Error fetching current price for {symbol}: {e}")
            return None

    def get_stock_info(self, symbol: str) -> Dict:
        """
        Get detailed stock information

        Args:
            symbol: Stock ticker symbol

        Returns:
            Dictionary with stock information
        """
        try:
            stock = yf.Ticker(symbol)
            info = stock.info

            return {
                'symbol': symbol,
                'name': info.get('longName', symbol),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'market_cap': info.get('marketCap', 'N/A'),
                'pe_ratio': info.get('trailingPE', 'N/A'),
                'dividend_yield': info.get('dividendYield', 'N/A'),
                '52w_high': info.get('fiftyTwoWeekHigh', 'N/A'),
                '52w_low': info.get('fiftyTwoWeekLow', 'N/A'),
            }
        except Exception as e:
            print(f"Error fetching info for {symbol}: {e}")
            return {'symbol': symbol, 'error': str(e)}

    def get_multiple_stocks(self, symbols: List[str], period: str = "1mo") -> Dict[str, pd.DataFrame]:
        """
        Fetch data for multiple stocks

        Args:
            symbols: List of stock ticker symbols
            period: Data period

        Returns:
            Dictionary mapping symbols to their DataFrames
        """
        results = {}

        for symbol in symbols:
            data = self.get_stock_data(symbol, period)
            if data is not None:
                results[symbol] = data

        return results
