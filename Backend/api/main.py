# Backend/api/main.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from scorer import AnomalyScorer

# ── FastAPI app ────────────────────────────────────────────────────────────────
app = FastAPI(
    title="S.E.N.T.R.Y. Anomaly Detection API",
    description="Scores transactions for anomalous behavior using a PyTorch autoencoder",
    version="1.0.0",
)

# ── CORS ───────────────────────────────────────────────────────────────────────
# This allows your Next.js frontend to call this API
# TODO: in production replace "*" with your actual frontend URL
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Load scorer once at startup ────────────────────────────────────────────────
# We load it once here so it doesn't reload the model on every request
scorer = AnomalyScorer()

# ── Request/Response Models ────────────────────────────────────────────────────
class Transaction(BaseModel):
    """
    The shape of a transaction sent from the frontend.
    All fields have defaults so you can test with partial data.
    TODO: add more fields as you expand your feature set
    """
    amount:             float = 0.5
    token_type:         int   = 0
    hour:               int   = 14
    day_of_week:        int   = 2
    gas_fee:            float = 0.002
    is_new_address:     int   = 0
    time_since_last_tx: int   = 3600
    tx_frequency:       int   = 2

class ScoreResponse(BaseModel):
    """
    The shape of the response sent back to the frontend.
    """
    risk_score:           float
    label:                str
    reconstruction_error: float
    threshold:            float
    features_used:        dict


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "S.E.N.T.R.Y. Anomaly Detection API is running"}


@app.get("/health")
def health():
    """
    Health check endpoint.
    Your frontend can ping this to check if the API is running.
    """
    return {"status": "healthy", "model_loaded": scorer is not None}


@app.post("/api/anomaly/score", response_model=ScoreResponse)
def score_transaction(transaction: Transaction):
    """
    Main endpoint — scores a single transaction.
    TODO: connect this to your frontend's dashboard
    
    Example request body:
    {
        "amount": 45.0,
        "token_type": 0,
        "hour": 3,
        "day_of_week": 1,
        "gas_fee": 0.09,
        "is_new_address": 1,
        "time_since_last_tx": 10,
        "tx_frequency": 35
    }
    """
    try:
        result = scorer.score(transaction.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/anomaly/score/batch")
def score_batch(transactions: list[Transaction]):
    """
    Batch endpoint — scores multiple transactions at once.
    Useful for loading the dashboard with historical data.
    TODO: connect to your dashboard's transaction table
    """
    try:
        results = [scorer.score(tx.dict()) for tx in transactions]
        return {"results": results, "count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/api/anomaly/random")
def get_random_transactions():
    """
    Returns 5 random transactions from the dataset with their scores.
    Used by the dashboard to show live-feeling data on refresh.
    """
    import pandas as pd
    import random

    df = pd.read_csv("../data/transactions.csv")
    sample = df.drop(columns=["label"]).sample(n=5).to_dict(orient="records")
    
    results = []
    for i, tx in enumerate(sample):
        score_result = scorer.score(tx)
        results.append({
            "id":          f"TX-{str(i+1).zfill(3)}",
            "token":       ["ETH", "USDC", "WBTC", "DAI"][int(tx["token_type"])],
            "amount":      tx["amount"],
            "time": f"{int(tx['hour']):02d}:00",
            "destination": random.choice([
                "0xaB3f...221C", "0x9f2A...88BD",
                "0x1122...AABB", "0x5544...33CC", "0xDEAD...BEEF"
            ]),
            "risk_score":  score_result["risk_score"],
            "label":       score_result["label"],
            "reconstruction_error": score_result["reconstruction_error"],
        })
    
    return {"transactions": results, "count": len(results)}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)