"""
Notification system for stock alerts
"""
from datetime import datetime
from typing import Dict, List
from colorama import Fore, Back, Style, init

# Initialize colorama for cross-platform colored output
init(autoreset=True)


class Notifier:
    """Handles notifications for stock alerts and insights"""

    def __init__(self, config: Dict):
        self.console_enabled = config.get('enable_console', True)
        self.email_enabled = config.get('enable_email', False)
        self.email_address = config.get('email_address', '')

    def format_price(self, price: float) -> str:
        """Format price with currency symbol"""
        return f"${price:,.2f}"

    def format_percentage(self, percentage: float) -> str:
        """Format percentage with color coding"""
        if percentage > 0:
            return f"{Fore.GREEN}+{percentage:.2f}%{Style.RESET_ALL}"
        elif percentage < 0:
            return f"{Fore.RED}{percentage:.2f}%{Style.RESET_ALL}"
        else:
            return f"{percentage:.2f}%"

    def get_signal_color(self, signal: str) -> str:
        """Get color for signal type"""
        if signal == 'BUY':
            return Fore.GREEN
        elif signal == 'SELL':
            return Fore.RED
        else:
            return Fore.YELLOW

    def print_separator(self, char: str = "=", length: int = 80):
        """Print a separator line"""
        if self.console_enabled:
            print(char * length)

    def print_header(self, text: str):
        """Print a formatted header"""
        if self.console_enabled:
            self.print_separator()
            print(f"{Fore.CYAN}{Style.BRIGHT}{text}{Style.RESET_ALL}")
            self.print_separator()

    def notify_daily_insights(self, analyses: List[Dict], insights: Dict):
        """
        Send daily insights notification

        Args:
            analyses: List of stock analyses
            insights: Portfolio insights
        """
        if not self.console_enabled:
            return

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.print_header(f"DAILY STOCK INSIGHTS - {timestamp}")

        print(f"\n{Fore.CYAN}Portfolio Overview:{Style.RESET_ALL}")
        print(f"  Total Stocks Analyzed: {insights['total_stocks']}")
        print(f"  {Fore.GREEN}BUY Signals: {insights['buy_signals']}{Style.RESET_ALL}")
        print(f"  {Fore.RED}SELL Signals: {insights['sell_signals']}{Style.RESET_ALL}")
        print(f"  {Fore.YELLOW}HOLD Signals: {insights['hold_signals']}{Style.RESET_ALL}")

        # Show all stock details
        print(f"\n{Fore.CYAN}Individual Stock Analysis:{Style.RESET_ALL}")
        for analysis in analyses:
            self._print_stock_analysis(analysis)

        # Top recommendations
        if insights['top_buys']:
            print(f"\n{Fore.GREEN}{Style.BRIGHT}TOP BUY RECOMMENDATIONS:{Style.RESET_ALL}")
            for i, stock in enumerate(insights['top_buys'], 1):
                print(f"  {i}. {stock['symbol']} - Confidence: {stock['recommendation']['confidence']:.1f}%")

        if insights['top_sells']:
            print(f"\n{Fore.RED}{Style.BRIGHT}TOP SELL RECOMMENDATIONS:{Style.RESET_ALL}")
            for i, stock in enumerate(insights['top_sells'], 1):
                print(f"  {i}. {stock['symbol']} - Confidence: {stock['recommendation']['confidence']:.1f}%")

        self.print_separator()

    def notify_realtime_alert(self, analysis: Dict):
        """
        Send real-time alert notification

        Args:
            analysis: Stock analysis
        """
        if not self.console_enabled:
            return

        signal = analysis['recommendation']['signal']

        if signal == 'HOLD':
            return  # Don't send alerts for HOLD signals in real-time

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        signal_color = self.get_signal_color(signal)

        print(f"\n{Back.WHITE}{Fore.BLACK} ALERT {Style.RESET_ALL} "
              f"{signal_color}{Style.BRIGHT}{signal} SIGNAL{Style.RESET_ALL} - "
              f"{timestamp}")

        self._print_stock_analysis(analysis, compact=False)

    def _print_stock_analysis(self, analysis: Dict, compact: bool = True):
        """
        Print formatted stock analysis

        Args:
            analysis: Stock analysis dictionary
            compact: Whether to use compact format
        """
        symbol = analysis['symbol']
        price = self.format_price(analysis['price'])
        change_1d = self.format_percentage(analysis['price_change_1d'])

        rec = analysis['recommendation']
        signal = rec['signal']
        signal_color = self.get_signal_color(signal)
        confidence = rec['confidence']

        print(f"\n{Fore.CYAN}{Style.BRIGHT}{symbol}{Style.RESET_ALL}")
        print(f"  Price: {price} ({change_1d} today)")

        if analysis['price_change_5d']:
            change_5d = self.format_percentage(analysis['price_change_5d'])
            print(f"  5-Day Change: {change_5d}")

        print(f"  Recommendation: {signal_color}{Style.BRIGHT}{signal}{Style.RESET_ALL} "
              f"(Confidence: {confidence:.1f}%)")

        if not compact or signal != 'HOLD':
            print(f"  Technical Indicators:")
            print(f"    RSI: {rec['rsi']:.2f}")
            print(f"    SMA Short: {self.format_price(rec['sma_short'])}")
            print(f"    SMA Long: {self.format_price(rec['sma_long'])}")
            print(f"    MACD: {rec['macd']:.4f} (Signal: {rec['macd_signal']:.4f})")

            print(f"  Analysis:")
            for reason in rec['reasons']:
                print(f"    • {reason}")

    def notify_error(self, message: str):
        """
        Send error notification

        Args:
            message: Error message
        """
        if self.console_enabled:
            print(f"{Fore.RED}{Style.BRIGHT}ERROR:{Style.RESET_ALL} {message}")

    def notify_info(self, message: str):
        """
        Send info notification

        Args:
            message: Info message
        """
        if self.console_enabled:
            print(f"{Fore.BLUE}INFO:{Style.RESET_ALL} {message}")

    def notify_success(self, message: str):
        """
        Send success notification

        Args:
            message: Success message
        """
        if self.console_enabled:
            print(f"{Fore.GREEN}SUCCESS:{Style.RESET_ALL} {message}")
