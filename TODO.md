# Trading AI MVP TODO
Tracking progress on SMC-based trading assistant.

## Phase 1: Project Structure & Setup [x]
- [x] Create backend/ directories and files (core/, mt5_client.py, etc.)
- [x] Create requirements.txt for backend
- [x] Create frontend/ basic dashboard
- [x] Update README.md with setup instructions
- [x] Create .gitignore, .env templates

## Phase 2: Backend Core Logic [x]
- [x] Implement trend_detector.py (HH/HL, LH/LL)
- [x] Implement structure.py (swings, BOS, MSS/CHOCH)
- [x] Implement zones.py (Order Blocks, FVG, Demand/Supply validation)
- [x] Implement liquidity.py (sweeps, equal highs/lows)
- [x] Implement signals.py (multi-TF logic, entry/SL/TP calc)
- [x] risk_manager.py (2 trades/day, RR 1:2+, BE, partials, 1-2% risk, drawdown killswitch)

## Phase 3: MT5 Integration & API [x]
- [x] mt5_client.py (fetch OHLC for 4H/1H/15M/5M, EURUSD/GBPUSD)
- [x] main.py FastAPI app (/analyze, /signals websocket)
- [x] explanations.py (human-like trade reasons)
- [x] config.py + .env (MT5 creds, Telegram token)

## Phase 4: Frontend Dashboard [x]
- [x] Basic HTML/JS dashboard with TradingView + API calls

## Phase 5: Notifications & Testing [ ]
- [ ] Telegram bot for alerts
- [ ] Unit tests
- [ ] Manual MT5 test

**Backend MVP complete. Test with `cd backend && uvicorn app.main:app --host 127.0.0.1 --port 8001` then frontend/index.html. Provide MT5 demo creds in .env to fetch live data.**

