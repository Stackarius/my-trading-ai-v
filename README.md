# my-trading-ai
# Trading AI MVP - SMC Demand/Supply Assistant

AI-powered trading assistant using Smart Money Concepts (SMC), multi-timeframe analysis, integrated with MT5.

## Quick Start

1. Install MT5 terminal, enable algo trading/DLL imports, login to demo account.

2. Backend:
```
cd backend
pip install -r requirements.txt
cp ../.env.example ../.env  # Edit with your MT5/Telegram creds
uvicorn app.main:app --reload --port 8000
```

3. Frontend (HTML/JS dashboard):\n```\n# Open directly\nstart frontend/index.html\n```

4. Test API: http://localhost:8000/docs

## Features
- HTF trend + BOS + Order Blocks
- LTF confirmation (MSS, liquidity sweep)
- Risk-managed signals (1:2+ RR)
- Telegram alerts

See TODO.md for progress.

