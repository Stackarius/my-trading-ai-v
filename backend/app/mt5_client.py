import MetaTrader5 as mt5
import pandas as pd
from .config import MT5_LOGIN, MT5_PASSWORD, MT5_SERVER, MT5_PATH, PAIRS
from typing import Optional
import logging
import os
import platform

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MT5Client:
    def __init__(self):
        self._initialized = False

    def _get_mt5_path(self) -> Optional[str]:
        """Locate MetaTrader 5 terminal executable path."""
        # First, check if MT5_PATH is explicitly configured
        if MT5_PATH and os.path.exists(MT5_PATH):
            logger.info(f"Using MT5 path from config: {MT5_PATH}")
            return MT5_PATH
        
        if platform.system() == "Windows":
            common_paths = [
                r"C:\Program Files\MetaTrader 5\terminal.exe",
                r"C:\Program Files (x86)\MetaTrader 5\terminal.exe",
                os.path.expanduser(r"~\AppData\Local\Apps\MetaTrader 5\terminal.exe"),
            ]
            for path in common_paths:
                if os.path.exists(path):
                    logger.info(f"Found MT5 terminal at: {path}")
                    return path
        logger.warning("MT5 terminal path not found in common locations.")
        return None

    def _ensure_connected(self):
        if not self._initialized:
            mt5_path = self._get_mt5_path()
            
            try:
                if mt5_path:
                    result = mt5.initialize(
                        path=mt5_path,
                        login=MT5_LOGIN,
                        password=MT5_PASSWORD,
                        server=MT5_SERVER,
                        timeout=5000
                    )
                else:
                    result = mt5.initialize(
                        login=MT5_LOGIN,
                        password=MT5_PASSWORD,
                        server=MT5_SERVER,
                        timeout=5000
                    )
                
                if not result:
                    error_msg = mt5.last_error()
                    logger.error(f"MT5 init failed: {error_msg}")
                    try:
                        mt5.shutdown()
                    except:
                        pass
                    raise RuntimeError(f"MT5 initialization failed: {error_msg}")
                
                self._initialized = True
                logger.info("MT5 connection established successfully")
                
            except Exception as e:
                logger.error(f"MT5 connection error: {e}")
                self._initialized = False
                raise

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
        client._ensure_connected()
    else:
        try:
            term_info = mt5.terminal_info()
            if term_info is None:
                logger.warning("MT5 terminal connection lost, attempting reconnect...")
                try:
                    client.close()
                except Exception as e:
                    logger.warning(f"Error closing stale connection: {e}")
                client = MT5Client()
                client._ensure_connected()
        except Exception as e:
            logger.warning(f"Connection check failed: {e}, reconnecting...")
            try:
                client.close()
            except:
                pass
            client = MT5Client()
            client._ensure_connected()
    
    return client

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
