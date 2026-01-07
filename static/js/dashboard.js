// Stock Picker Dashboard JavaScript

let socket;
let currentAnalyses = [];

// Toast Notification System
function showToast(message, type = 'info', duration = 5000) {
    const toastContainer = document.getElementById('toast-container');
    const toastId = 'toast-' + Date.now();

    const bgClass = {
        'success': 'bg-success',
        'error': 'bg-danger',
        'warning': 'bg-warning',
        'info': 'bg-info'
    }[type] || 'bg-info';

    const icon = {
        'success': 'bi-check-circle-fill',
        'error': 'bi-exclamation-circle-fill',
        'warning': 'bi-exclamation-triangle-fill',
        'info': 'bi-info-circle-fill'
    }[type] || 'bi-info-circle-fill';

    const toastHTML = `
        <div id="${toastId}" class="toast align-items-center text-white ${bgClass} border-0" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="bi ${icon} me-2"></i>${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;

    toastContainer.insertAdjacentHTML('beforeend', toastHTML);
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, { delay: duration });
    toast.show();

    // Remove from DOM after hiding
    toastElement.addEventListener('hidden.bs.toast', () => {
        toastElement.remove();
    });
}

// Initialize Socket.IO connection
function initializeSocket() {
    socket = io();

    socket.on('connect', () => {
        console.log('Connected to server');
        updateConnectionStatus(true);
    });

    socket.on('disconnect', () => {
        console.log('Disconnected from server');
        updateConnectionStatus(false);
    });

    socket.on('connected', (data) => {
        console.log(data.message);
    });

    socket.on('analysis_update', (data) => {
        console.log('Received analysis update:', data);
        updateDashboard(data);
    });
}

// Update connection status indicator
function updateConnectionStatus(connected) {
    const statusIcon = document.getElementById('status-icon');
    const statusText = document.getElementById('status-text');

    if (connected) {
        statusIcon.className = 'bi bi-circle-fill text-success status-connected';
        statusText.textContent = 'Connected';
    } else {
        statusIcon.className = 'bi bi-circle-fill text-danger status-disconnected';
        statusText.textContent = 'Disconnected';
    }
}

// Refresh analysis
document.getElementById('refresh-btn').addEventListener('click', async () => {
    const btn = document.getElementById('refresh-btn');
    btn.disabled = true;
    btn.innerHTML = '<i class="bi bi-arrow-clockwise spinner-border spinner-border-sm"></i> Analyzing...';

    console.log('Starting stock analysis...');
    showToast('Fetching stock data...', 'info', 3000);

    try {
        const response = await fetch('/api/analyze');
        console.log('Response status:', response.status);

        const data = await response.json();
        console.log('Response data:', data);

        if (data.success) {
            console.log('Analysis successful!', data);
            showToast(`Successfully analyzed ${data.analyses.length} stocks!`, 'success');
            updateDashboard(data);
        } else {
            console.error('Analysis failed:', data.message);
            showToast('Analysis failed: ' + data.message, 'error', 7000);
        }
    } catch (error) {
        console.error('Error during analysis:', error);
        showToast('Network error. Please check your connection and try again.', 'error', 7000);
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-arrow-clockwise"></i> Refresh Analysis';
    }
});

// Update dashboard with new data
function updateDashboard(data) {
    currentAnalyses = data.analyses;

    // Update timestamp
    const timestamp = new Date(data.timestamp);
    document.getElementById('last-updated').textContent = timestamp.toLocaleString();

    // Update overview cards
    document.getElementById('total-stocks').textContent = data.insights.total_stocks;
    document.getElementById('buy-signals').textContent = data.insights.buy_signals;
    document.getElementById('sell-signals').textContent = data.insights.sell_signals;
    document.getElementById('hold-signals').textContent = data.insights.hold_signals;

    // Update top recommendations
    updateTopRecommendations(data.insights);

    // Update stock cards
    updateStockCards(data.analyses);
}

// Update top recommendations
function updateTopRecommendations(insights) {
    const topBuysContainer = document.getElementById('top-buys');
    const topSellsContainer = document.getElementById('top-sells');

    // Top Buys
    if (insights.top_buys && insights.top_buys.length > 0) {
        topBuysContainer.innerHTML = insights.top_buys.map((stock, index) => `
            <div class="recommendation-item buy">
                <span class="symbol">${index + 1}. ${stock.symbol}</span>
                <span class="confidence">${stock.recommendation.confidence.toFixed(1)}%</span>
                <div class="mt-2">
                    <small>$${stock.price.toFixed(2)}</small>
                    <span class="ms-2 ${stock.price_change_1d >= 0 ? 'text-success' : 'text-danger'}">
                        ${stock.price_change_1d >= 0 ? '+' : ''}${stock.price_change_1d.toFixed(2)}%
                    </span>
                </div>
            </div>
        `).join('');
    } else {
        topBuysContainer.innerHTML = '<p class="text-muted">No buy signals detected</p>';
    }

    // Top Sells
    if (insights.top_sells && insights.top_sells.length > 0) {
        topSellsContainer.innerHTML = insights.top_sells.map((stock, index) => `
            <div class="recommendation-item sell">
                <span class="symbol">${index + 1}. ${stock.symbol}</span>
                <span class="confidence">${stock.recommendation.confidence.toFixed(1)}%</span>
                <div class="mt-2">
                    <small>$${stock.price.toFixed(2)}</small>
                    <span class="ms-2 ${stock.price_change_1d >= 0 ? 'text-success' : 'text-danger'}">
                        ${stock.price_change_1d >= 0 ? '+' : ''}${stock.price_change_1d.toFixed(2)}%
                    </span>
                </div>
            </div>
        `).join('');
    } else {
        topSellsContainer.innerHTML = '<p class="text-muted">No sell signals detected</p>';
    }
}

// Update stock cards
function updateStockCards(analyses) {
    const container = document.getElementById('stock-cards');

    if (!analyses || analyses.length === 0) {
        container.innerHTML = '<div class="col-12"><p class="text-muted">No stock data available</p></div>';
        return;
    }

    container.innerHTML = analyses.map(stock => {
        const rec = stock.recommendation;
        const signalClass = rec.signal.toLowerCase();
        const priceChangeClass = stock.price_change_1d >= 0 ? 'positive' : 'negative';

        return `
            <div class="col-md-6 col-lg-4">
                <div class="card stock-card fade-in" onclick="showStockDetails('${stock.symbol}')">
                    <div class="card-body">
                        <h5 class="card-title">${stock.symbol}</h5>
                        <div class="stock-price">
                            $${stock.price.toFixed(2)}
                            <span class="price-change ${priceChangeClass}">
                                ${stock.price_change_1d >= 0 ? '+' : ''}${stock.price_change_1d.toFixed(2)}%
                            </span>
                        </div>
                        ${stock.price_change_5d !== null ? `
                            <div class="text-muted" style="font-size: 0.9rem;">
                                5d: ${stock.price_change_5d >= 0 ? '+' : ''}${stock.price_change_5d.toFixed(2)}%
                            </div>
                        ` : ''}

                        <div class="signal-badge ${signalClass}">
                            ${rec.signal}
                        </div>

                        <div class="mt-2">
                            <small class="text-muted">Confidence: ${rec.confidence.toFixed(1)}%</small>
                            <div class="confidence-bar">
                                <div class="confidence-fill ${signalClass}" style="width: ${rec.confidence}%"></div>
                            </div>
                        </div>

                        <div class="indicators">
                            <div class="indicator">
                                <span class="indicator-label">RSI:</span> ${rec.rsi.toFixed(1)}
                            </div>
                            <div class="indicator">
                                <span class="indicator-label">MACD:</span> ${rec.macd.toFixed(3)}
                            </div>
                        </div>

                        <div class="analysis-reasons">
                            <small class="text-muted">Analysis:</small>
                            <ul style="font-size: 0.85rem; margin-top: 5px;">
                                ${rec.reasons.slice(0, 3).map(reason => `<li>${reason}</li>`).join('')}
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

// Show stock details in modal
async function showStockDetails(symbol) {
    const modal = new bootstrap.Modal(document.getElementById('stockModal'));
    document.getElementById('modalStockSymbol').textContent = `${symbol} - Detailed Analysis`;

    // Show loading state
    document.getElementById('stock-chart').innerHTML = '<div class="spinner-container"><div class="spinner-border" role="status"></div></div>';
    document.getElementById('modal-indicators').innerHTML = '<p>Loading...</p>';
    document.getElementById('modal-info').innerHTML = '<p>Loading...</p>';

    modal.show();

    try {
        // Fetch chart data
        const chartResponse = await fetch(`/api/stock/${symbol}/chart?period=3mo`);
        const chartData = await chartResponse.json();

        if (chartData.success) {
            Plotly.newPlot('stock-chart', chartData.chart.data, chartData.chart.layout);

            // Update indicators
            const stock = currentAnalyses.find(s => s.symbol === symbol);
            if (stock) {
                const rec = stock.recommendation;
                document.getElementById('modal-indicators').innerHTML = `
                    <table class="table table-sm">
                        <tr><td>RSI</td><td>${rec.rsi.toFixed(2)}</td></tr>
                        <tr><td>SMA Short</td><td>$${rec.sma_short.toFixed(2)}</td></tr>
                        <tr><td>SMA Long</td><td>$${rec.sma_long.toFixed(2)}</td></tr>
                        <tr><td>MACD</td><td>${rec.macd.toFixed(4)}</td></tr>
                        <tr><td>MACD Signal</td><td>${rec.macd_signal.toFixed(4)}</td></tr>
                    </table>
                `;
            }
        }

        // Fetch stock info
        const infoResponse = await fetch(`/api/stock/${symbol}/info`);
        const infoData = await infoResponse.json();

        if (infoData.success) {
            const info = infoData.info;
            document.getElementById('modal-info').innerHTML = `
                <table class="table table-sm">
                    <tr><td>Name</td><td>${info.name || 'N/A'}</td></tr>
                    <tr><td>Sector</td><td>${info.sector || 'N/A'}</td></tr>
                    <tr><td>Industry</td><td>${info.industry || 'N/A'}</td></tr>
                    <tr><td>52w High</td><td>${info['52w_high'] !== 'N/A' ? '$' + info['52w_high'].toFixed(2) : 'N/A'}</td></tr>
                    <tr><td>52w Low</td><td>${info['52w_low'] !== 'N/A' ? '$' + info['52w_low'].toFixed(2) : 'N/A'}</td></tr>
                    <tr><td>P/E Ratio</td><td>${info.pe_ratio !== 'N/A' ? info.pe_ratio.toFixed(2) : 'N/A'}</td></tr>
                </table>
            `;
        }
    } catch (error) {
        console.error('Error loading stock details:', error);
        document.getElementById('stock-chart').innerHTML = '<p class="text-danger">Error loading chart</p>';
    }
}

// Dark Mode functionality
function initializeDarkMode() {
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    const themeIcon = document.getElementById('theme-icon');
    const htmlElement = document.documentElement;

    // Check for saved theme preference or default to 'light' mode
    const currentTheme = localStorage.getItem('theme') || 'light';
    htmlElement.setAttribute('data-theme', currentTheme);

    // Update icon based on current theme
    updateThemeIcon(currentTheme);

    // Toggle dark mode on button click
    darkModeToggle.addEventListener('click', () => {
        const newTheme = htmlElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
        htmlElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateThemeIcon(newTheme);

        // Show toast notification
        showToast(`Switched to ${newTheme} mode`, 'info', 2000);
    });

    function updateThemeIcon(theme) {
        if (theme === 'dark') {
            themeIcon.className = 'bi bi-sun-fill';
        } else {
            themeIcon.className = 'bi bi-moon-stars-fill';
        }
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeDarkMode();
    initializeSocket();
});
