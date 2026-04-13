from typing import Dict, Any

import pandas as pd
from .trend_detector import get_recent_swings
from .zones import detect_fvg

def detect_bos(df: pd.DataFrame, direction: str, window: int = 5) -> bool:
    """Break of Structure: New high > prev swing high (bull BOS), low < prev low (bear)."""
    swings = get_recent_swings(df, window)
    if direction == "bull":
        return swings["last_swing_high"][1] > swings["prev_swing_high"][1]
    elif direction == "bear":
        return swings["last_swing_low"][1] < swings["prev_swing_low"][1]
    return False

def detect_mss(df: pd.DataFrame, htf_trend: str, window: int = 5) -> str:
    """Market Structure Shift / CHOCH: LTF breaks opposite to HTF."""
    swings = get_recent_swings(df, window)
    ltf_trend = swings["trend"]
    
    if htf_trend == "uptrend" and ltf_trend == "downtrend":
        return "bear_mss"  # Potential reversal or confirmation fail
    elif htf_trend == "downtrend" and ltf_trend == "uptrend":
        return "bull_mss"
    return "no_mss"

