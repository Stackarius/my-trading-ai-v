import pandas as pd
from typing import List, Dict
from .trend_detector import find_swings

def detect_liquidity_sweeps(df: pd.DataFrame, swings: list) -> List[Dict]:
    """Liquidity sweep: Price goes beyond swing high/low then reverses."""
    sweeps = []
    tolerance = 0.0001  # Pip tolerance
    
    for swing_time, swing_price in swings[-10:]:
        idx = df.index.get_loc(swing_time)
        post_swing = df.iloc[idx+1:idx+20]  # Next 20 bars
        
        if len(post_swing) == 0:
            continue
            
        # High sweep
        if post_swing['high'].max() > swing_price * (1 + tolerance):
            sweeps.append({'type': 'high_liquidity_swept', 'level': swing_price, 'time': post_swing.index[0]})
        # Low sweep
        elif post_swing['low'].min() < swing_price * (1 - tolerance):
            sweeps.append({'type': 'low_liquidity_swept', 'level': swing_price, 'time': post_swing.index[0]})
    
    return sweeps

def has_equal_highs_lows(df: pd.DataFrame, tolerance: float = 0.00005) -> Dict:
    """Equal highs/lows for internal liquidity."""
    highs = df['high'].rolling(5).max()
    lows = df['low'].rolling(5).min()
    
    eq_highs = (highs.diff().abs() < tolerance).sum() > 2
    eq_lows = (lows.diff().abs() < tolerance).sum() > 2
    
    return {'equal_highs': eq_highs, 'equal_lows': eq_lows}

