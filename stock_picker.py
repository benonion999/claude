"""
Main Stock Picker Application
Provides daily insights and real-time stock recommendations
"""
import json
import time
from datetime import datetime
from typing import Dict, List
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from stock_fetcher import StockDataFetcher
from stock_analyzer import StockAnalyzer
from notifier import Notifier


class StockPicker:
    """Main application for stock picking with daily insights and real-time monitoring"""

    def __init__(self, config_path: str = "config.json"):
        """
        Initialize the stock picker

        Args:
            config_path: Path to configuration file
        """
        self.config = self.load_config(config_path)
        self.fetcher = StockDataFetcher()
        self.analyzer = StockAnalyzer(self.config['analysis_settings'])
        self.notifier = Notifier(self.config['notification_settings'])
        self.scheduler = BackgroundScheduler()
        self.previous_signals = {}  # Track previous signals to detect changes
        self.running = False

    def load_config(self, config_path: str) -> Dict:
        """
        Load configuration from JSON file

        Args:
            config_path: Path to config file

        Returns:
            Configuration dictionary
        """
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            raise

    def analyze_all_stocks(self) -> tuple[List[Dict], Dict]:
        """
        Analyze all configured stocks

        Returns:
            Tuple of (analyses list, insights dictionary)
        """
        stocks = self.config['stocks']
        self.notifier.notify_info(f"Analyzing {len(stocks)} stocks...")

        # Fetch data for all stocks
        stock_data = self.fetcher.get_multiple_stocks(stocks, period="3mo")

        # Analyze each stock
        analyses = []
        for symbol, data in stock_data.items():
            try:
                analysis = self.analyzer.analyze_stock(symbol, data)
                analyses.append(analysis)
            except Exception as e:
                self.notifier.notify_error(f"Error analyzing {symbol}: {e}")

        # Generate portfolio insights
        insights = self.analyzer.get_portfolio_insights(analyses)

        return analyses, insights

    def daily_insights_job(self):
        """Job that runs daily to provide insights"""
        self.notifier.notify_info("Running daily insights analysis...")

        try:
            analyses, insights = self.analyze_all_stocks()
            self.notifier.notify_daily_insights(analyses, insights)

            # Update previous signals for comparison
            for analysis in analyses:
                symbol = analysis['symbol']
                self.previous_signals[symbol] = analysis['recommendation']['signal']

        except Exception as e:
            self.notifier.notify_error(f"Daily insights job failed: {e}")

    def realtime_monitoring_job(self):
        """Job that runs at intervals for real-time monitoring"""
        try:
            stocks = self.config['stocks']

            for symbol in stocks:
                # Fetch recent data
                data = self.fetcher.get_stock_data(symbol, period="1mo", interval="1d")

                if data is None:
                    continue

                # Analyze
                analysis = self.analyzer.analyze_stock(symbol, data)
                current_signal = analysis['recommendation']['signal']

                # Check if signal changed or is strong BUY/SELL
                previous_signal = self.previous_signals.get(symbol, 'HOLD')

                if current_signal != previous_signal:
                    # Signal changed - send alert
                    self.notifier.notify_realtime_alert(analysis)
                    self.previous_signals[symbol] = current_signal
                elif current_signal in ['BUY', 'SELL'] and analysis['recommendation']['confidence'] > 70:
                    # Strong signal - send alert
                    self.notifier.notify_realtime_alert(analysis)

        except Exception as e:
            self.notifier.notify_error(f"Real-time monitoring failed: {e}")

    def schedule_jobs(self):
        """Schedule daily and real-time monitoring jobs"""
        # Parse daily update time
        daily_time = self.config['daily_update_time']
        hour, minute = map(int, daily_time.split(':'))

        # Schedule daily insights
        self.scheduler.add_job(
            self.daily_insights_job,
            CronTrigger(hour=hour, minute=minute),
            id='daily_insights',
            name='Daily Stock Insights'
        )

        # Schedule real-time monitoring
        check_interval = self.config['check_interval_minutes']
        self.scheduler.add_job(
            self.realtime_monitoring_job,
            'interval',
            minutes=check_interval,
            id='realtime_monitoring',
            name='Real-time Stock Monitoring'
        )

        self.notifier.notify_success(f"Scheduled daily insights at {daily_time}")
        self.notifier.notify_success(f"Scheduled real-time monitoring every {check_interval} minutes")

    def run_once(self):
        """Run analysis once immediately"""
        self.notifier.notify_info("Running one-time analysis...")
        self.daily_insights_job()

    def start(self):
        """Start the stock picker with scheduled jobs"""
        self.notifier.print_header("STOCK PICKER STARTED")

        # Run initial analysis
        self.run_once()

        # Schedule jobs
        self.schedule_jobs()

        # Start scheduler
        self.scheduler.start()
        self.running = True

        self.notifier.notify_info("Stock Picker is running. Press Ctrl+C to stop.")

        try:
            # Keep the main thread alive
            while self.running:
                time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            self.stop()

    def stop(self):
        """Stop the stock picker"""
        self.notifier.notify_info("Stopping Stock Picker...")
        self.scheduler.shutdown()
        self.running = False
        self.notifier.notify_success("Stock Picker stopped")


def main():
    """Main entry point"""
    picker = StockPicker()
    picker.start()


if __name__ == "__main__":
    main()
