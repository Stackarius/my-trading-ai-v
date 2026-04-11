import MetaTrader5 as mt5
import pandas as pd
from .config import MT5_LOGIN, MT5_PASSWORD, MT5_SERVER, PAIRS
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MT5Client:
    def __init__(self):
        self._initialized = False

    def _ensure_connected(self):
        if not self._initialized:
            if not mt5.initialize(login=MT5_LOGIN, password=MT5_PASSWORD, server=MT5_SERVER):
                logger.error(f"MT5 init failed: {mt5.last_error()}")
                raise RuntimeError("MT5 initialization failed")
            self._initialized = True

    def get_ohlc(self, symbol: str, timeframe: str, count: int = 500) -> Optional[pd.DataFrame]:
        """Fetch OHLC data. Timeframes: '4H', '1H', '15M', '5M' mapped to MT5."""
        self._ensure_connected()

        tf_map = {
            '4H': mt5.TIMEFRAME_H4,
            '1H': mt5.TIMEFRAME_H1,
            '15M': mt5.TIMEFRAME_M15,
            '5M': mt5.TIMEFRAME_M5
        }

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
        if self._initialized:
            mt5.shutdown()
            self._initialized = False


# Global client singleton
client = None


def get_client() -> MT5Client:
    global client
    if client is None:
        client = MT5Client()
    else:
        # Check if MT5 terminal is still alive, reconnect if not
        if not mt5.terminal_info():
            logger.warning("MT5 connection lost, reconnecting...")
            try:
                client.close()
            except Exception:
                pass
            client = MT5Client()
    return client