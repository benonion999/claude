"""
Web application for Stock Picker with real-time dashboard
"""
import json
import threading
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS

from stock_fetcher import StockDataFetcher
from stock_analyzer import StockAnalyzer
from notifier import Notifier
import plotly.graph_objs as go
import plotly.utils


app = Flask(__name__)
app.config['SECRET_KEY'] = 'stock-picker-secret-key'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Global state
config = {}
fetcher = None
analyzer = None
latest_analyses = []
alert_history = []


def get_default_config():
    """Get default configuration"""
    return {
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
            "enable_console": True,
            "enable_email": False,
            "email_address": ""
        }
    }


def load_config():
    """Load configuration from file or use defaults"""
    global config, fetcher, analyzer
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
            print("Loaded configuration from config.json")
    except FileNotFoundError:
        print("config.json not found, using default configuration")
        config = get_default_config()
        # Try to save default config
        try:
            with open('config.json', 'w') as f:
                json.dump(config, f, indent=2)
                print("Created config.json with default settings")
        except Exception as e:
            print(f"Could not create config.json: {e} (continuing with defaults)")
    except Exception as e:
        print(f"Error loading config: {e}, using defaults")
        config = get_default_config()

    try:
        fetcher = StockDataFetcher()
        analyzer = StockAnalyzer(config['analysis_settings'])
        return True
    except Exception as e:
        print(f"Error initializing fetcher/analyzer: {e}")
        return False


def save_config():
    """Save configuration to file"""
    try:
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False


@app.route('/')
def index():
    """Render main dashboard"""
    return render_template('index.html')


@app.route('/health')
def health():
    """Health check endpoint for deployment platforms"""
    return jsonify({'status': 'healthy', 'service': 'stock-picker'}), 200


@app.route('/api/test-yfinance')
def test_yfinance():
    """Test if yfinance is working with custom headers"""
    try:
        print("Testing yfinance with AAPL using custom headers...")
        # Use the fetcher's session with headers
        data = fetcher.get_stock_data("AAPL", period="5d")

        if data is None or data.empty:
            return jsonify({
                'success': False,
                'message': 'yfinance returned empty data for AAPL even with custom headers',
                'rows': 0,
                'note': 'Yahoo Finance may be blocking requests from this server IP'
            }), 500

        return jsonify({
            'success': True,
            'message': 'yfinance is working with custom headers!',
            'symbol': 'AAPL',
            'rows': len(data),
            'latest_price': float(data['Close'].iloc[-1]),
            'data_sample': data.tail(2).to_dict()
        })
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'message': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/settings')
def settings():
    """Render settings page"""
    return render_template('settings.html')


@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration"""
    return jsonify(config)


@app.route('/api/config', methods=['POST'])
def update_config():
    """Update configuration"""
    global config, analyzer
    try:
        new_config = request.json
        config.update(new_config)
        analyzer = StockAnalyzer(config['analysis_settings'])
        save_config()
        return jsonify({'success': True, 'message': 'Configuration updated'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


@app.route('/api/stocks', methods=['GET'])
def get_stocks():
    """Get list of tracked stocks"""
    return jsonify({'stocks': config.get('stocks', [])})


@app.route('/api/analyze', methods=['GET'])
def analyze_stocks():
    """Analyze all stocks and return results"""
    global latest_analyses

    try:
        print("Starting stock analysis...")
        stocks = config.get('stocks', [])

        if not stocks:
            print("No stocks configured!")
            return jsonify({
                'success': False,
                'message': 'No stocks configured. Please add stocks in settings.'
            }), 400

        print(f"Analyzing stocks: {stocks}")
        stock_data = fetcher.get_multiple_stocks(stocks, period="3mo")
        print(f"Fetched data for {len(stock_data)} stocks")

        if not stock_data:
            print("No stock data returned from fetcher")
            return jsonify({
                'success': False,
                'message': 'Failed to fetch stock data. Please check your internet connection and try again.'
            }), 500

        analyses = []
        for symbol, data in stock_data.items():
            try:
                print(f"Analyzing {symbol}...")
                analysis = analyzer.analyze_stock(symbol, data)
                analyses.append(analysis)
                print(f"Successfully analyzed {symbol}")
            except Exception as e:
                print(f"Error analyzing {symbol}: {e}")
                import traceback
                traceback.print_exc()

        if not analyses:
            print("No successful analyses")
            return jsonify({
                'success': False,
                'message': 'Failed to analyze stocks. Please try again.'
            }), 500

        # Generate insights
        print("Generating portfolio insights...")
        insights = analyzer.get_portfolio_insights(analyses)

        # Store latest analyses
        latest_analyses = analyses

        # Emit update to all connected clients
        try:
            socketio.emit('analysis_update', {
                'analyses': analyses,
                'insights': insights,
                'timestamp': datetime.now().isoformat()
            })
            print("Emitted WebSocket update")
        except Exception as e:
            print(f"Error emitting WebSocket update: {e}")

        print(f"Analysis complete! Returning {len(analyses)} analyses")
        return jsonify({
            'success': True,
            'analyses': analyses,
            'insights': insights,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        print(f"Fatal error in analyze_stocks: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/stock/<symbol>/chart', methods=['GET'])
def get_stock_chart(symbol):
    """Get chart data for a specific stock"""
    try:
        period = request.args.get('period', '1mo')
        data = fetcher.get_stock_data(symbol, period=period)

        if data is None:
            return jsonify({'success': False, 'message': 'No data available'}), 404

        # Calculate indicators
        df = analyzer.calculate_indicators(data)

        # Create candlestick chart
        candlestick = go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='Price'
        )

        # Add moving averages
        sma_short = go.Scatter(
            x=df.index,
            y=df['SMA_Short'],
            name=f'SMA {config["analysis_settings"]["sma_short_period"]}',
            line=dict(color='blue', width=1)
        )

        sma_long = go.Scatter(
            x=df.index,
            y=df['SMA_Long'],
            name=f'SMA {config["analysis_settings"]["sma_long_period"]}',
            line=dict(color='orange', width=1)
        )

        # Volume chart
        colors = ['red' if df['Close'].iloc[i] < df['Open'].iloc[i] else 'green'
                  for i in range(len(df))]

        volume = go.Bar(
            x=df.index,
            y=df['Volume'],
            name='Volume',
            marker=dict(color=colors),
            yaxis='y2'
        )

        # Create figure with secondary y-axis
        fig = go.Figure(data=[candlestick, sma_short, sma_long, volume])

        fig.update_layout(
            title=f'{symbol} Stock Price',
            yaxis=dict(title='Price ($)'),
            yaxis2=dict(title='Volume', overlaying='y', side='right'),
            xaxis=dict(title='Date'),
            hovermode='x unified',
            height=500
        )

        # Convert to JSON
        chart_json = json.loads(plotly.utils.PlotlyJSONEncoder().encode(fig))

        return jsonify({
            'success': True,
            'chart': chart_json,
            'current_price': float(df['Close'].iloc[-1]),
            'rsi': float(df['RSI'].iloc[-1])
        })

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/stock/<symbol>/info', methods=['GET'])
def get_stock_info(symbol):
    """Get detailed information for a stock"""
    try:
        info = fetcher.get_stock_info(symbol)
        return jsonify({'success': True, 'info': info})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """Get alert history"""
    return jsonify({'alerts': alert_history})


@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    emit('connected', {'message': 'Connected to Stock Picker'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')


@socketio.on('request_update')
def handle_update_request():
    """Handle client request for update"""
    if latest_analyses:
        insights = analyzer.get_portfolio_insights(latest_analyses)
        emit('analysis_update', {
            'analyses': latest_analyses,
            'insights': insights,
            'timestamp': datetime.now().isoformat()
        })


def run_web_app(host='0.0.0.0', port=5000, debug=False):
    """Run the web application"""
    load_config()
    print(f"Starting Stock Picker Web Dashboard on http://{host}:{port}")
    socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)


# Load config on module import for production deployment
load_config()

if __name__ == '__main__':
    run_web_app(debug=True)
