import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# Trading parameters
INITIAL_BALANCE = float(os.getenv("INITIAL_BALANCE", 10000))
LOT_SIZE = float(os.getenv("LOT_SIZE", 0.01))
MAX_POSITIONS = int(os.getenv("MAX_POSITIONS", 3))
INTERVAL_MINUTES = int(os.getenv("INTERVAL_MINUTES", 30))

# Backtesting
BACKTEST_DAYS = int(os.getenv("BACKTEST_DAYS", 30))
OPTIMIZATION_SCHEDULE = os.getenv("OPTIMIZATION_SCHEDULE", "sunday at 00:00")

# Forex pairs (format untuk Finnhub OANDA)
FOREX_PAIRS = ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CAD", "NZD/USD", "USD/CHF"]

# ZF Parameters
LAMBDA_INITIAL = 0.1
STOP_LOSS_SIGMA = 3.0
ADX_THRESHOLD = 25
REGIME_LOOKBACK = 50
