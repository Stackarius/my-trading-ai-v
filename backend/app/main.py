from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import logging
import os

from .core.signals import analyze_symbol
from .explanations import generate_explanation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: pre-warm MT5 connection
    try:
        from .mt5_client import get_client
        get_client()  # Test call to ensure MT5 is responsive
        logger.info(" MT5 connected successfully x 1")
    except Exception as e:
        logger.warning(f"  MT5 not available at startup: {e} — will retry on first request")
    yield
    # Shutdown: clean up MT5 connection
    try:
        from .mt5_client import client
        if client:
            client.close()
            logger.info(" MT5 disconnected cleanly")
    except Exception:
        pass


app = FastAPI(title="Trading AI MVP", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    """Serve the frontend dashboard"""
    frontend_path = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "index.html")
    if os.path.exists(frontend_path):
        return FileResponse(frontend_path, media_type="text/html")
    return {"message": "Trading AI SMC Backend - Ready for HTF/LTF analysis"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/analyze/{symbol}/{htf_tf}")
async def analyze(symbol: str, htf_tf: str):
    try:
        analysis = analyze_symbol(symbol, htf_tf)
        if analysis.get("signal"):
            analysis["explanation"] = generate_explanation(analysis)
        return analysis
    except Exception as e:
        logger.error(f"Analysis error for {symbol}/{htf_tf}: {e}")
        return {"error": str(e)}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
