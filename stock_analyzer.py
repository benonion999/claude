"""
Stock analysis engine for generating buy/sell recommendations
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator, EMAIndicator, MACD
from ta.volume import VolumeWeightedAveragePrice


class StockAnalyzer:
    """Analyzes stock data and provides buy/sell recommendations"""

    def __init__(self, config: Dict):
        self.rsi_oversold = config.get('rsi_oversold', 30)
        self.rsi_overbought = config.get('rsi_overbought', 70)
        self.sma_short = config.get('sma_short_period', 20)
        self.sma_long = config.get('sma_long_period', 50)
        self.volume_spike_threshold = config.get('volume_spike_threshold', 1.5)

    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate technical indicators for stock data

        Args:
            data: Stock price DataFrame from yfinance

        Returns:
            DataFrame with added technical indicators
        """
        df = data.copy()

        # RSI (Relative Strength Index)
        rsi = RSIIndicator(close=df['Close'], window=14)
        df['RSI'] = rsi.rsi()

        # Simple Moving Averages
        sma_short = SMAIndicator(close=df['Close'], window=self.sma_short)
        sma_long = SMAIndicator(close=df['Close'], window=self.sma_long)
        df['SMA_Short'] = sma_short.sma_indicator()
        df['SMA_Long'] = sma_long.sma_indicator()

        # Exponential Moving Averages
        ema_12 = EMAIndicator(close=df['Close'], window=12)
        ema_26 = EMAIndicator(close=df['Close'], window=26)
        df['EMA_12'] = ema_12.ema_indicator()
        df['EMA_26'] = ema_26.ema_indicator()

        # MACD (Moving Average Convergence Divergence)
        macd = MACD(close=df['Close'])
        df['MACD'] = macd.macd()
        df['MACD_Signal'] = macd.macd_signal()
        df['MACD_Diff'] = macd.macd_diff()

        # Volume analysis
        df['Volume_MA'] = df['Volume'].rolling(window=20).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Volume_MA']

        return df

    def generate_signals(self, data: pd.DataFrame) -> Dict:
        """
        Generate buy/sell signals based on technical indicators

        Args:
            data: DataFrame with calculated indicators

        Returns:
            Dictionary containing signals and recommendations
        """
        if len(data) < self.sma_long:
            return {
                'signal': 'HOLD',
                'confidence': 0,
                'reasons': ['Insufficient data for analysis']
            }

        latest = data.iloc[-1]
        prev = data.iloc[-2]

        signals = []
        buy_score = 0
        sell_score = 0

        # RSI Analysis
        if latest['RSI'] < self.rsi_oversold:
            signals.append(f"RSI oversold ({latest['RSI']:.2f}) - Potential buy signal")
            buy_score += 2
        elif latest['RSI'] > self.rsi_overbought:
            signals.append(f"RSI overbought ({latest['RSI']:.2f}) - Potential sell signal")
            sell_score += 2

        # Moving Average Crossover
        if latest['SMA_Short'] > latest['SMA_Long'] and prev['SMA_Short'] <= prev['SMA_Long']:
            signals.append(f"Golden Cross: SMA{self.sma_short} crossed above SMA{self.sma_long} - Strong buy signal")
            buy_score += 3
        elif latest['SMA_Short'] < latest['SMA_Long'] and prev['SMA_Short'] >= prev['SMA_Long']:
            signals.append(f"Death Cross: SMA{self.sma_short} crossed below SMA{self.sma_long} - Strong sell signal")
            sell_score += 3

        # Price vs Moving Averages
        if latest['Close'] > latest['SMA_Short'] > latest['SMA_Long']:
            signals.append("Price above both moving averages - Bullish trend")
            buy_score += 1
        elif latest['Close'] < latest['SMA_Short'] < latest['SMA_Long']:
            signals.append("Price below both moving averages - Bearish trend")
            sell_score += 1

        # MACD Analysis
        if latest['MACD'] > latest['MACD_Signal'] and prev['MACD'] <= prev['MACD_Signal']:
            signals.append("MACD bullish crossover - Buy signal")
            buy_score += 2
        elif latest['MACD'] < latest['MACD_Signal'] and prev['MACD'] >= prev['MACD_Signal']:
            signals.append("MACD bearish crossover - Sell signal")
            sell_score += 2

        # Volume Analysis
        if latest['Volume_Ratio'] > self.volume_spike_threshold:
            signals.append(f"Volume spike detected ({latest['Volume_Ratio']:.2f}x average) - Increased activity")
            if buy_score > sell_score:
                buy_score += 1
            else:
                sell_score += 1

        # Determine overall signal
        total_score = buy_score + sell_score
        if total_score == 0:
            signal = 'HOLD'
            confidence = 0
        else:
            confidence = abs(buy_score - sell_score) / total_score * 100

            if buy_score > sell_score:
                signal = 'BUY'
            elif sell_score > buy_score:
                signal = 'SELL'
            else:
                signal = 'HOLD'

        return {
            'signal': signal,
            'confidence': round(confidence, 2),
            'buy_score': buy_score,
            'sell_score': sell_score,
            'reasons': signals if signals else ['No strong signals detected'],
            'current_price': latest['Close'],
            'rsi': latest['RSI'],
            'sma_short': latest['SMA_Short'],
            'sma_long': latest['SMA_Long'],
            'macd': latest['MACD'],
            'macd_signal': latest['MACD_Signal']
        }

    def analyze_stock(self, symbol: str, data: pd.DataFrame) -> Dict:
        """
        Complete analysis for a single stock

        Args:
            symbol: Stock ticker symbol
            data: Stock price DataFrame

        Returns:
            Dictionary with complete analysis
        """
        df_with_indicators = self.calculate_indicators(data)
        signals = self.generate_signals(df_with_indicators)

        # Calculate price changes
        latest_price = df_with_indicators['Close'].iloc[-1]
        price_change_1d = ((latest_price - df_with_indicators['Close'].iloc[-2]) /
                          df_with_indicators['Close'].iloc[-2] * 100)

        if len(df_with_indicators) >= 5:
            price_change_5d = ((latest_price - df_with_indicators['Close'].iloc[-5]) /
                              df_with_indicators['Close'].iloc[-5] * 100)
        else:
            price_change_5d = None

        return {
            'symbol': symbol,
            'price': latest_price,
            'price_change_1d': round(price_change_1d, 2),
            'price_change_5d': round(price_change_5d, 2) if price_change_5d else None,
            'recommendation': signals
        }

    def get_portfolio_insights(self, analyses: List[Dict]) -> Dict:
        """
        Generate insights across multiple stocks

        Args:
            analyses: List of stock analyses

        Returns:
            Portfolio-level insights
        """
        buy_recommendations = [a for a in analyses if a['recommendation']['signal'] == 'BUY']
        sell_recommendations = [a for a in analyses if a['recommendation']['signal'] == 'SELL']

        # Sort by confidence
        buy_recommendations.sort(key=lambda x: x['recommendation']['confidence'], reverse=True)
        sell_recommendations.sort(key=lambda x: x['recommendation']['confidence'], reverse=True)

        return {
            'total_stocks': len(analyses),
            'buy_signals': len(buy_recommendations),
            'sell_signals': len(sell_recommendations),
            'hold_signals': len(analyses) - len(buy_recommendations) - len(sell_recommendations),
            'top_buys': buy_recommendations[:3],
            'top_sells': sell_recommendations[:3]
        }
