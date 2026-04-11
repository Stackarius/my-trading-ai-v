import pandas as pd
from typing import Dict, Any, Optional
from ..mt5_client import get_client
from .trend_detector import find_swings, get_recent_swings
from .structure import detect_bos, detect_mss
from .zones import identify_order_block, detect_fvg, validate_zone
from .liquidity import detect_liquidity_sweeps, has_equal_highs_lows
from ..config import PAIRS, MAX_TRADES_PER_DAY, MAX_RISK_PCT, MIN_RR

TF_MAP = {"4H": "15M", "1H": "5M"}  # HTF -> LTF

def analyze_symbol(symbol: str, htf_tf: str) -> Dict[str, Any]:
    """Full analysis: HTF trend/BOS/OB -> LTF confirm."""
    if symbol not in PAIRS:
        return {"error": "Invalid pair"}
    
    client = get_client()
    htf_df = client.get_ohlc(symbol, htf_tf)
    ltf_tf = TF_MAP.get(htf_tf, "5M")
    ltf_df = client.get_ohlc(symbol, ltf_tf)
    
    if htf_df is None or ltf_df is None:
        return {"error": "Data fetch failed"}
    
    # HTF
    swings = get_recent_swings(htf_df)
    htf_trend = swings["trend"]
    if htf_trend == "neutral":
        return {"trend": "neutral", "signal": None}
    
    htf_bos = detect_bos(htf_df, "bull" if htf_trend == "uptrend" else "bear")
    htf_obs = identify_order_block(htf_df, htf_trend)
    valid_obs = [ob for ob in htf_obs if validate_zone(ob, detect_fvg(htf_df))]
    
    if not htf_bos or not valid_obs:
        return {"trend": htf_trend, "valid_setup": False, "signal": None}
    
    # Check mitigation: price near last valid OB
    last_ob = valid_obs[-1]
    current_price = htf_df['close'].iloc[-1]
    mitigation = abs(current_price - (last_ob['top'] + last_ob['bottom'])/2) / current_price < 0.002  # 0.2%
    
    if not mitigation:
        return {"trend": htf_trend, "mitigation": False, "signal": None}
    
    # LTF Confirmation
    ltf_mss = detect_mss(ltf_df, htf_trend)
    ltf_obs = identify_order_block(ltf_df, htf_trend)
    ltf_fvgs = detect_fvg(ltf_df)
    ltf_valid = any(validate_zone(ob, ltf_fvgs) for ob in ltf_obs)
    ltf_swings = find_swings(ltf_df)
    liquidity_sweeps = detect_liquidity_sweeps(ltf_df, ltf_swings[0] + ltf_swings[1])
    liq_swept = len(liquidity_sweeps) > 0
    
    if ltf_mss != "no_mss" and ltf_valid and liq_swept:
        direction = "BUY" if htf_trend == "uptrend" else "SELL"
        entry = (last_ob['top'] + last_ob['bottom'])/2  # LTF OB avg
        swing_key = "last_swing_low" if direction=="BUY" else "last_swing_high"
        swing = ltf_swings.get(swing_key)
        sl = swing[1] if swing else entry * (0.995 if direction=="BUY" else 1.005)
        tp_dist = abs(entry - sl) * MIN_RR
        tp = entry + tp_dist if direction=="BUY" else entry - tp_dist
        
        return {
            "trend": htf_trend,
            "htf_zone": {
                **last_ob,
                "time": str(last_ob['time'])
            },
            "ltf_confirm": True,
            "signal": {
                "action": direction,
                "entry": round(entry, 5),
                "sl": round(sl, 5),
                "tp": round(tp, 5),
                "rr": MIN_RR
            }
        }
    
    return {"trend": htf_trend, "ltf_confirm": False, "signal": None}

# Global trade count for risk (in-memory MVP)
daily_trades = 0

