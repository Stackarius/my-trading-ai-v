import pandas as pd
from typing import Dict, Any, Optional
from .mt5_client import get_client
from .trend_detector import detect_trend, get_recent_swings
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
    
    try:
        client = get_client()
        htf_df = client.get_ohlc(symbol, htf_tf)
        ltf_tf = TF_MAP.get(htf_tf, "5M")
        ltf_df = client.get_ohlc(symbol, ltf_tf)
        
        if htf_df is None or ltf_df is None:
            return {"error": "Data fetch failed"}
        
        # HTF Analysis
        swings = get_recent_swings(htf_df)
        htf_trend = swings["trend"]
        if htf_trend == "neutral":
            return {"trend": "neutral", "signal": None}
        
        # Get entry point and stop loss from swings
        if htf_trend == "uptrend":
            if swings["last_swing_low"] is None:
                return {"trend": htf_trend, "valid_setup": False, "signal": None}
            entry = swings["last_swing_low"][1]
            sl = swings["prev_swing_low"][1] if swings["prev_swing_low"] else entry * 0.995
            direction = "BUY"
        else:  # downtrend
            if swings["last_swing_high"] is None:
                return {"trend": htf_trend, "valid_setup": False, "signal": None}
            entry = swings["last_swing_high"][1]
            sl = swings["prev_swing_high"][1] if swings["prev_swing_high"] else entry * 1.005
            direction = "SELL"
        
        # Calculate TP from risk/reward ratio
        tp_dist = abs(entry - sl) * MIN_RR
        tp = entry + tp_dist if direction == "BUY" else entry - tp_dist
        
        # Get current price
        current_price = htf_df['close'].iloc[-1]
        
        # Basic validation: entry should be reasonable relative to current price
        entry_distance = abs(current_price - entry) / current_price
        if entry_distance > 0.05:  # Entry more than 5% away is unrealistic
            return {
                "trend": htf_trend,
                "signal": None,
                "reason": "Entry point too far from current price"
            }
        
        # LTF Confirmation (optional enhancement)
        ltf_swings = get_recent_swings(ltf_df)
        ltf_trend = ltf_swings["trend"]
        
        # Signal is stronger if LTF confirms HTF
        ltf_confirms = (direction == "BUY" and ltf_trend in ["uptrend", "neutral"]) or \
                       (direction == "SELL" and ltf_trend in ["downtrend", "neutral"])
        
        return {
            "trend": htf_trend,
            "htf_zone": last_ob,
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
                "rr": MIN_RR,
                "distance_pips": round(abs(current_price - entry) * 10000, 1)  # For FX
            }
        }
    
    except Exception as e:
        import logging
        logging.error(f"Error in analyze_symbol: {e}", exc_info=True)
        return {"error": f"Analysis failed: {str(e)}"}



# Global trade count for risk (in-memory MVP)
daily_trades = 0

