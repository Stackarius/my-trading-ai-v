from typing import Dict
from ..config import MAX_TRADES_PER_DAY, MAX_RISK_PCT, MIN_RR

daily_trades = 0
account_balance = 100000  # Mock

def can_trade() -> bool:
    global daily_trades
    return daily_trades < MAX_TRADES_PER_DAY

def calc_position_size(entry: float, sl: float, balance: float = account_balance) -> float:
    risk_amount = balance * MAX_RISK_PCT
    pip_risk = abs(entry - sl) / 0.0001  # Assume 5-digit
    lot_size = risk_amount / (pip_risk * 10)  # $10/pip per lot
    return round(lot_size, 2)

def check_rr(entry: float, sl: float, tp: float) -> float:
    risk = abs(entry - sl)
    reward = abs(tp - entry)
    return reward / risk if risk > 0 else 0

def execute_trade(signal: Dict, balance: float) -> Dict:
    if not can_trade() or check_rr(signal['entry'], signal['sl'], signal['tp']) < MIN_RR:
        return {"error": "Risk rules violated"}
    
    global daily_trades
    daily_trades += 1
    pos_size = calc_position_size(signal['entry'], signal['sl'], balance)
    
    # Mock MT5 order
    return {
        "status": "executed",
        "ticket": 12345,
        "size": pos_size,
        "be_pending": False  # Set at 1:1 later
    }

