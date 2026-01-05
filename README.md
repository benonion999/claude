# Stock Picker - Automated Stock Analysis & Alerts

A Python-based stock analysis tool that provides daily insights and real-time buy/sell recommendations based on technical indicators.

## Features

- **Web Dashboard**: Beautiful, modern web interface with real-time updates
- **Interactive Charts**: Candlestick charts with technical indicators using Plotly
- **Daily Insights**: Scheduled daily stock analysis reports at a configured time
- **Real-time Monitoring**: Continuous monitoring with alerts on signal changes
- **Technical Analysis**: Uses RSI, SMA, EMA, MACD, and volume analysis
- **Buy/Sell Recommendations**: Automated recommendations with confidence scores
- **Configurable**: Easy web-based settings or JSON configuration
- **Dual Mode**: Run as web dashboard or console application
- **WebSocket Updates**: Live updates pushed to dashboard automatically

## Technical Indicators Used

- **RSI (Relative Strength Index)**: Identifies overbought/oversold conditions
- **SMA (Simple Moving Average)**: Detects trend direction and crossovers
- **EMA (Exponential Moving Average)**: Provides weighted recent price data
- **MACD (Moving Average Convergence Divergence)**: Momentum and trend indicator
- **Volume Analysis**: Detects unusual trading activity

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. Clone or navigate to the repository:
```bash
cd /home/user/claude
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

Edit `config.json` to customize your settings:

```json
{
  "stocks": ["ASML", "NVDA", "AMD", "TSMC"],
  "daily_update_time": "09:00",
  "check_interval_minutes": 15,
  "analysis_settings": {
    "rsi_oversold": 30,
    "rsi_overbought": 70,
    "sma_short_period": 20,
    "sma_long_period": 50,
    "volume_spike_threshold": 1.5
  },
  "notification_settings": {
    "enable_console": true,
    "enable_email": false,
    "email_address": ""
  }
}
```

### Configuration Options

- **stocks**: Array of stock ticker symbols to monitor
- **daily_update_time**: Time for daily insights (24-hour format HH:MM)
- **check_interval_minutes**: Frequency of real-time checks (in minutes)
- **analysis_settings**:
  - `rsi_oversold`: RSI threshold for oversold condition (default: 30)
  - `rsi_overbought`: RSI threshold for overbought condition (default: 70)
  - `sma_short_period`: Short-term SMA period (default: 20 days)
  - `sma_long_period`: Long-term SMA period (default: 50 days)
  - `volume_spike_threshold`: Volume spike multiplier (default: 1.5x average)

## Usage

Stock Picker can run in two modes: **Web Dashboard** (recommended) or **Console Mode**.

### Web Dashboard Mode (Recommended)

Start the web-based dashboard:

```bash
python run.py --mode web
```

Or simply:

```bash
python run.py
```

Then open your browser to: **http://localhost:5000**

#### Web Dashboard Features:

- **Portfolio Overview**: Visual cards showing total stocks, buy/sell/hold signals
- **Top Recommendations**: Prioritized buy and sell suggestions with confidence scores
- **Stock Cards**: Interactive cards for each stock with current analysis
- **Detailed Charts**: Click any stock to view candlestick charts with technical indicators
- **Real-time Updates**: Live updates via WebSocket (no manual refresh needed)
- **Settings Page**: Configure stocks and analysis parameters through the web UI
- **Responsive Design**: Works on desktop, tablet, and mobile devices

#### Custom Host/Port:

```bash
python run.py --mode web --host 0.0.0.0 --port 8080
```

### Console Mode

For terminal-based operation with colored text output:

```bash
python run.py --mode console
```

Or directly:

```bash
python stock_picker.py
```

The application will:
1. Run an initial analysis immediately
2. Schedule daily insights at your configured time
3. Monitor stocks in real-time at the configured interval
4. Display alerts when buy/sell signals change or are strong

### Stopping the Application

Press `Ctrl+C` to gracefully stop the stock picker in either mode.

## Deployment to Live URL

Want to access your Stock Picker from anywhere? Deploy it to a live URL!

See the complete **[Deployment Guide](DEPLOYMENT.md)** for step-by-step instructions to deploy on:
- **Render.com** (Recommended - Free tier available)
- Railway.app
- Fly.io
- Heroku

Quick deploy to Render:
1. Push code to GitHub
2. Sign up at https://render.com
3. Create Web Service from your GitHub repo
4. Use start command: `gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT web_app:app`
5. Get your live URL in minutes!

## Understanding the Output

### Signal Types

- **BUY**: Bullish indicators suggest buying opportunity
- **SELL**: Bearish indicators suggest selling opportunity
- **HOLD**: Mixed or neutral signals, no action recommended

### Confidence Score

The confidence score (0-100%) indicates how strong the signal is based on the number and strength of technical indicators aligned in the same direction.

### Example Output

```
================================================================================
DAILY STOCK INSIGHTS - 2026-01-05 09:00:00
================================================================================

Portfolio Overview:
  Total Stocks Analyzed: 4
  BUY Signals: 2
  SELL Signals: 1
  HOLD Signals: 1

Individual Stock Analysis:

ASML
  Price: $875.42 (+2.34% today)
  5-Day Change: +5.67%
  Recommendation: BUY (Confidence: 75.0%)
  Technical Indicators:
    RSI: 45.32
    SMA Short: $865.20
    SMA Long: $850.10
    MACD: 2.4521 (Signal: 1.8932)
  Analysis:
    • Price above both moving averages - Bullish trend
    • MACD bullish crossover - Buy signal
    • Volume spike detected (1.8x average) - Increased activity
```

## How It Works

1. **Data Fetching**: Uses yfinance API to fetch historical and real-time stock data
2. **Technical Analysis**: Calculates multiple technical indicators on the data
3. **Signal Generation**: Evaluates indicators to generate buy/sell signals with confidence scores
4. **Scheduling**: APScheduler runs jobs at configured intervals
5. **Notifications**: Colored console output displays insights and alerts

## Project Structure

```
.
├── config.json           # Configuration file
├── requirements.txt      # Python dependencies
├── run.py               # Main launcher (web or console mode)
├── stock_picker.py      # Console application
├── web_app.py           # Flask web application
├── stock_fetcher.py     # Stock data fetching module
├── stock_analyzer.py    # Technical analysis engine
├── notifier.py          # Notification system (console)
├── templates/           # HTML templates
│   ├── index.html       # Main dashboard
│   └── settings.html    # Settings page
├── static/              # Static web assets
│   ├── css/
│   │   └── style.css    # Custom styling
│   └── js/
│       ├── dashboard.js # Dashboard functionality
│       └── settings.js  # Settings functionality
└── README.md            # This file
```

## Customization

### Using Web Settings (Easy Method)

1. Navigate to **http://localhost:5000/settings** in your browser
2. Modify any settings through the user-friendly interface
3. Click "Save Configuration"
4. Changes take effect immediately

### Manual Configuration (Advanced)

Edit `config.json` directly:

#### Adding More Stocks

```json
{
  "stocks": ["ASML", "NVDA", "AMD", "TSMC", "AAPL", "MSFT", "GOOGL"]
}
```

#### Adjusting Analysis Parameters

Modify `analysis_settings` to tune the sensitivity of signals:

- Lower RSI thresholds = more sensitive to overbought/oversold
- Shorter SMA periods = more responsive to price changes
- Higher volume threshold = only alert on larger volume spikes

#### Changing Schedule

- **Daily insights**: Modify `daily_update_time` (e.g., "16:00" for 4 PM)
- **Real-time checks**: Modify `check_interval_minutes` (e.g., 5 for every 5 minutes)

## Limitations & Disclaimers

- **Not Financial Advice**: This tool is for educational and informational purposes only
- **Technical Analysis Only**: Does not consider fundamental analysis, news, or market sentiment
- **Historical Data**: Past performance does not guarantee future results
- **API Limitations**: yfinance has rate limits; avoid very frequent requests
- **Market Hours**: Some features work best during market hours

## Troubleshooting

### No data returned for stock

- Verify the ticker symbol is correct
- Check your internet connection
- Ensure the stock is publicly traded

### Jobs not running at scheduled time

- Verify the time format in config.json (24-hour HH:MM)
- Check system timezone settings
- Ensure the application remains running

### Import errors

- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Verify Python version (3.8+): `python --version`

## Future Enhancements

Potential features for future versions:

- Email/SMS notifications
- Backtesting capabilities with historical performance metrics
- Machine learning price predictions
- Portfolio tracking with buy/sell transaction history
- News sentiment analysis integration
- Support for cryptocurrency and forex markets
- Multi-user support with authentication
- Mobile app (iOS/Android)
- Webhook notifications for third-party integrations
- Advanced charting with drawing tools

## License

This project is provided as-is for educational purposes.

## Support

For issues or questions, please check the configuration and ensure all dependencies are properly installed.
