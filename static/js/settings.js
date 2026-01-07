// Stock Picker Settings JavaScript

let currentConfig = {};

// Load configuration on page load
async function loadConfiguration() {
    try {
        const response = await fetch('/api/config');
        const config = await response.json();
        currentConfig = config;

        // Populate form fields
        document.getElementById('stocks-input').value = config.stocks.join(', ');
        document.getElementById('daily-time-input').value = config.daily_update_time;
        document.getElementById('interval-input').value = config.check_interval_minutes;

        // Analysis settings
        document.getElementById('rsi-oversold').value = config.analysis_settings.rsi_oversold;
        document.getElementById('rsi-overbought').value = config.analysis_settings.rsi_overbought;
        document.getElementById('sma-short').value = config.analysis_settings.sma_short_period;
        document.getElementById('sma-long').value = config.analysis_settings.sma_long_period;
        document.getElementById('volume-threshold').value = config.analysis_settings.volume_spike_threshold;

    } catch (error) {
        console.error('Error loading configuration:', error);
        showMessage('Error loading configuration', 'danger');
    }
}

// Save configuration
document.getElementById('save-btn').addEventListener('click', async () => {
    const btn = document.getElementById('save-btn');
    btn.disabled = true;
    btn.innerHTML = '<i class="bi bi-hourglass-split"></i> Saving...';

    try {
        // Gather form data
        const stocksInput = document.getElementById('stocks-input').value;
        const stocks = stocksInput.split(',').map(s => s.trim()).filter(s => s.length > 0);

        const updatedConfig = {
            stocks: stocks,
            daily_update_time: document.getElementById('daily-time-input').value,
            check_interval_minutes: parseInt(document.getElementById('interval-input').value),
            analysis_settings: {
                rsi_oversold: parseInt(document.getElementById('rsi-oversold').value),
                rsi_overbought: parseInt(document.getElementById('rsi-overbought').value),
                sma_short_period: parseInt(document.getElementById('sma-short').value),
                sma_long_period: parseInt(document.getElementById('sma-long').value),
                volume_spike_threshold: parseFloat(document.getElementById('volume-threshold').value)
            },
            notification_settings: currentConfig.notification_settings || {
                enable_console: true,
                enable_email: false,
                email_address: ''
            }
        };

        // Validate
        if (stocks.length === 0) {
            showMessage('Please enter at least one stock symbol', 'danger');
            return;
        }

        if (updatedConfig.analysis_settings.sma_short_period >= updatedConfig.analysis_settings.sma_long_period) {
            showMessage('Short SMA period must be less than Long SMA period', 'danger');
            return;
        }

        // Save configuration
        const response = await fetch('/api/config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(updatedConfig)
        });

        const result = await response.json();

        if (result.success) {
            showMessage('Configuration saved successfully!', 'success');
            currentConfig = updatedConfig;
        } else {
            showMessage('Error saving configuration: ' + result.message, 'danger');
        }

    } catch (error) {
        console.error('Error saving configuration:', error);
        showMessage('Error saving configuration', 'danger');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-save"></i> Save Configuration';
    }
});

// Show message
function showMessage(message, type) {
    const messageDiv = document.getElementById('save-message');
    messageDiv.className = `alert alert-${type}`;
    messageDiv.textContent = message;
    messageDiv.style.display = 'block';

    // Auto-hide after 5 seconds
    setTimeout(() => {
        messageDiv.style.display = 'none';
    }, 5000);
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

        showMessage(`Switched to ${newTheme} mode`, 'info');
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
    loadConfiguration();
});
