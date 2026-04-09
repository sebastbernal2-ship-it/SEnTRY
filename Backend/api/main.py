# Backend/api/main.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv
import os
import traceback
import pandas as pd
import random

# Load env vars
load_dotenv()

import logging

# Setup logging
logging.basicConfig(filename="api_errors.log", level=logging.ERROR)

from scorer import AnomalyScorer
from manipulation_scorer import ManipulationScorer

# --- FastAPI app ---
app = FastAPI(
    title="S.E.N.T.R.Y. Anomaly Detection API",
    description="Scores transactions for anomalous behavior using a PyTorch autoencoder",
    version="1.0.0",
)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Load scorer once at startup ---
scorer = AnomalyScorer()
try:
    manipulation_scorer = ManipulationScorer()
except Exception as e:
    logging.error(f"Failed to load ManipulationScorer: {e}")
    manipulation_scorer = None

# --- Request/Response Models ---
class Transaction(BaseModel):
    amount:             float = 0.5
    token_type:         int   = 0
    hour:               int   = 14
    day_of_week:        int   = 2
    gas_fee:            float = 0.002
    is_new_address:     int   = 0
    time_since_last_tx: int   = 3600
    tx_frequency:       int   = 2

class ScoreResponse(BaseModel):
    risk_score:           float
    label:                str
    reconstruction_error: float
    threshold:            float
    features_used:        dict

class Proposal(BaseModel):
    agent_id: str
    size: float
    success: bool

# --- Routes ---

@app.get("/")
def root():
    return {"message": "S.E.N.T.R.Y. Anomaly Detection API is running"}

@app.get("/health")
def health():
    return {"status": "healthy", "model_loaded": scorer is not None}

@app.post("/api/anomaly/score", response_model=ScoreResponse)
def score_transaction(transaction: Transaction):
    try:
        result = scorer.score(transaction.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/anomaly/score/batch")
def score_batch(transactions: list[Transaction]):
    try:
        results = [scorer.score(tx.dict()) for tx in transactions]
        return {"results": results, "count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/api/anomaly/random")
def get_random_transactions():
    try:
        use_real = os.getenv("USE_REAL_DATA", "False").lower() == "true"
        default_path = "../data/transactions_real.csv" if use_real else "../data/transactions.csv"
        path = os.path.abspath(os.path.join(os.path.dirname(__file__), default_path))

        if not os.path.exists(path):
            raise HTTPException(status_code=404, detail=f"Data file not found at {path}")

        df = pd.read_csv(path)
        sample = df.drop(columns=["label"]).sample(n=min(5, len(df))).to_dict(orient="records")
        
        results = []
        for i, tx in enumerate(sample):
            score_result = scorer.score(tx)
            results.append({
                "id":          f"TX-{str(i+1).zfill(3)}",
                "token":       ["ETH", "USDC", "WBTC", "DAI"][int(tx["token_type"])],
                "amount":      tx["amount"],
                "time":        f"{int(tx['hour']):02d}:00",
                "destination": f"0x{os.urandom(20).hex()[:4]}...{os.urandom(20).hex()[:4]}",
                "risk_score":           score_result["risk_score"],
                "label":                score_result["label"],
                "reconstruction_error": score_result["reconstruction_error"],
            })
        
        return {"transactions": results, "count": len(results)}
    except Exception as e:
        logging.error(f"ERROR in /api/anomaly/random: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/manipulation/propose")
def log_proposal(proposal: Proposal):
    if not manipulation_scorer:
        raise HTTPException(status_code=500, detail="ManipulationScorer not loaded")
    try:
        manipulation_scorer.log_proposal(proposal.agent_id, proposal.size, proposal.success)
        return manipulation_scorer.score_agent(proposal.agent_id)
    except Exception as e:
        logging.error(f"ERROR in /api/manipulation/propose: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/manipulation/agents")
def get_agents():
    if not manipulation_scorer:
        raise HTTPException(status_code=500, detail="ManipulationScorer not loaded")
    try:
        return {"agents": manipulation_scorer.get_all_agents()}
    except Exception as e:
        logging.error(f"ERROR in /api/manipulation/agents: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
