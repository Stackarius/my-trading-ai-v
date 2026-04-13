import MetaTrader5 as mt5
import pandas as pd
from .config import MT5_LOGIN, MT5_PASSWORD, MT5_SERVER, PAIRS
from .core.trend_detector import get_recent_swings
from typing import Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MT5Client:
    def __init__(self):
        if not mt5.initialize(login=MT5_LOGIN, password=MT5_PASSWORD, server=MT5_SERVER):
            logger.error(f"MT5 init failed: {mt5.last_error()}")
            raise RuntimeError("MT5 initialization failed")

    def get_ohlc(self, symbol: str, timeframe: str, count: int = 500) -> Optional[pd.DataFrame]:
        """Fetch OHLC data. Timeframes: '4H', '1H', '15M', '5M' mapped to MT5."""
        tf_map = {'4H': mt5.TIMEFRAME_H4, '1H': mt5.TIMEFRAME_H1, '15M': mt5.TIMEFRAME_M15, '5M': mt5.TIMEFRAME_M5}
        
        if symbol not in PAIRS:
            logger.warning(f"Symbol {symbol} not in allowed pairs")
            return None
            
        tf = tf_map.get(timeframe)
        if not tf:
            return None
            
        rates = mt5.copy_rates_from_pos(symbol, tf, 0, count)
        if rates is None:
            logger.error(f"Failed to fetch {symbol} {timeframe}")
            return None
            
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)
        return df[['open', 'high', 'low', 'close', 'tick_volume']]

    def close(self):
        mt5.shutdown()

# Global client for MVP
client = None

def get_client():
    global client
    if client is None:
        client = MT5Client()
    return client

