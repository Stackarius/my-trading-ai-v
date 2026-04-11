import pandas as pd
import numpy as np
from typing import Tuple, List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

def find_swings(df: pd.DataFrame, window: int = 5) -> Tuple[List[Tuple], List[Tuple]]:
    """Detect swing highs/lows using local extrema."""
    highs = []
    lows = []
    
    high = df['high'].rolling(window=window, center=True).max()
    low = df['low'].rolling(window=window, center=True).min()
    
    for i in range(window, len(df) - window):
        if df['high'].iloc[i] == high.iloc[i]:
            highs.append((df.index[i], df['high'].iloc[i]))
        if df['low'].iloc[i] == low.iloc[i]:
            lows.append((df['low'].iloc[i], df['low'].iloc[i]))  # Fix: (time, low)
    
    return highs, lows

def detect_trend(swings_high: List[Tuple], swings_low: List[Tuple], lookback: int = 3) -> str:
    """Detect uptrend (HH/HL), downtrend (LH/LL), or neutral."""
    if len(swings_high) < lookback or len(swings_low) < lookback:
        return "neutral"
    
    recent_highs = swings_high[-lookback:]
    recent_lows = swings_low[-lookback:]
    
    # Uptrend: Higher highs and higher lows
    hh = all(recent_highs[i][1] > recent_highs[i-1][1] for i in range(1, lookback))
    hl = all(recent_lows[i][1] > recent_lows[i-1][1] for i in range(1, lookback))
    if hh and hl:
        return "uptrend"
    
    # Downtrend: Lower highs and lower lows
    lh = all(recent_highs[i][1] < recent_highs[i-1][1] for i in range(1, lookback))
    ll = all(recent_lows[i][1] < recent_lows[i-1][1] for i in range(1, lookback))
    if lh and ll:
        return "downtrend"
    
    return "neutral"

def get_recent_swings(df: pd.DataFrame, window: int = 5) -> Dict:
    highs, lows = find_swings(df, window)
    return {
        "last_swing_high": highs[-1] if highs else None,
        "last_swing_low": lows[-1] if lows else None,
        "prev_swing_high": highs[-2] if len(highs) > 1 else None,
        "prev_swing_low": lows[-2] if len(lows) > 1 else None,
        "trend": detect_trend(highs, lows)
    }

