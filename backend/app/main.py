from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from .core.signals import analyze_symbol
from .explanations import generate_explanation

app = FastAPI(title="Trading AI MVP", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Trading AI SMC Backend - Ready for HTF/LTF analysis"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/analyze/{symbol}/{htf_tf}")
async def analyze(symbol: str, htf_tf: str):
    try:
        analysis = analyze_symbol(symbol, htf_tf)
        if 'signal' in analysis:
            analysis['explanation'] = generate_explanation(analysis)
        return analysis
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

