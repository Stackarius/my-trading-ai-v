import os
from dotenv import load_dotenv

load_dotenv()

MT5_LOGIN = int(os.getenv("MT5_LOGIN", 0))
MT5_PASSWORD = os.getenv("MT5_PASSWORD", "")
MT5_SERVER = os.getenv("MT5_SERVER", "")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

PAIRS = ["EURUSD", "GBPUSD"]
MAX_TRADES_PER_DAY = 2
MAX_RISK_PCT = 0.02  # 2%
MIN_RR = 2.0

