import pandas as pd
import numpy as np
from typing import List, Tuple, Dict
from .trend_detector import find_swings

def detect_fvg(df: pd.DataFrame) -> List[Dict]:
    """Fair Value Gap: Imbalance gaps."""
    fvgs = []
    for i in range(2, len(df)):
        # Bull FVG: low[i] > high[i-2]
        if df['low'].iloc[i] > df['high'].iloc[i-2]:
            fvgs.append({
                'type': 'bull_fvg',
                'top': df['low'].iloc[i],
                'bottom': df['high'].iloc[i-2],
                'time': df.index[i]
            })
        # Bear FVG: high[i] < low[i-2]
        elif df['high'].iloc[i] < df['low'].iloc[i-2]:
            fvgs.append({
                'type': 'bear_fvg',
                'top': df['low'].iloc[i-2],
                'bottom': df['high'].iloc[i],
                'time': df.index[i]
            })
    return fvgs[-10:]  # Recent 10

def identify_order_block(df: pd.DataFrame, trend: str) -> List[Dict]:
    """Order Block: Last bearish candle before bull impulse (demand), vice versa."""
    from .structure import detect_bos

    obs = []
    body_size = (df['close'] - df['open']).abs()
    impulse_threshold = body_size.mean() * 1.5  # Strong move
    
    for i in range(10, len(df)):
        if trend == "uptrend":
            # Demand OB: Last red candle before green impulse
            if (df['close'].iloc[i-1] < df['open'].iloc[i-1] and  # Red candle
                df['close'].iloc[i] > df['open'].iloc[i] and body_size.iloc[i] > impulse_threshold):
                obs.append({
                    'type': 'demand',
                    'top': max(df['high'].iloc[i-1], df['open'].iloc[i-1]),
                    'bottom': min(df['low'].iloc[i-1], df['close'].iloc[i-1]),
                    'time': df.index[i-1],
                    'valid': detect_bos(df.iloc[:i], 'bull')  # BOS after
                })
        else:  # downtrend supply
            if (df['close'].iloc[i-1] > df['open'].iloc[i-1] and  # Green
                df['close'].iloc[i] < df['open'].iloc[i] and body_size.iloc[i] > impulse_threshold):
                obs.append({
                    'type': 'supply',
                    'top': max(df['high'].iloc[i-1], df['open'].iloc[i-1]),
                    'bottom': min(df['low'].iloc[i-1], df['close'].iloc[i-1]),
                    'time': df.index[i-1],
                    'valid': detect_bos(df.iloc[:i], 'bear')
                })
    return obs[-5:]  # Recent valid A+ setups

def validate_zone(ob: Dict, fvgs: List[Dict]) -> bool:
    """A+ zone: OB + FVG overlap + BOS."""
    if not ob['valid']:
        return False
    for fvg in fvgs:
        if (ob['bottom'] < fvg['top'] and ob['top'] > fvg['bottom']):  # Overlap
            return True
    return False

