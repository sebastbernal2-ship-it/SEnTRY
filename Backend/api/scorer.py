# Backend/api/scorer.py

import torch
import pickle
import numpy as np
import sys
import os
from dotenv import load_dotenv

# Load env vars
load_dotenv()

# add model folder to path so we can import Autoencoder
sys.path.append(os.path.join(os.path.dirname(__file__), "../model"))
from autoencoder import Autoencoder

# ── Paths ──────────────────────────────────────────────────────────────────────
MODEL_PATH  = os.path.join(os.path.dirname(__file__), "../data/saved_model.pth")
SCALER_PATH = os.path.join(os.path.dirname(__file__), "../data/scaler.pkl")
# ──────────────────────────────────────────────────────────────────────────────

# feature order must match exactly what was used during training
FEATURES = [
    "amount",
    "token_type",
    "hour",
    "day_of_week",
    "gas_fee",
    "is_new_address",
    "time_since_last_tx",
    "tx_frequency",
]


class AnomalyScorer:
    """
    Loads the trained autoencoder and scores new transactions.
    Converts raw reconstruction error into a 0-100 risk score.
    """

    def __init__(self):
        print("Loading model and scaler...")

        # ── Load saved model ───────────────────────────────────────────────
        checkpoint = torch.load(MODEL_PATH, map_location="cpu")
        self.input_dim = checkpoint["input_dim"]
        self.threshold = checkpoint["threshold"]

        self.model = Autoencoder(input_dim=self.input_dim)
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.model.eval()  # set to evaluation mode

        # ── Load scaler ────────────────────────────────────────────────────
        with open(SCALER_PATH, "rb") as f:
            self.scaler = pickle.load(f)

        print(f"Model loaded — anomaly threshold: {self.threshold:.6f}")

    def _extract_features(self, transaction: dict) -> np.ndarray:
        """
        Extracts features from a transaction dict in the correct order.
        TODO: add more feature engineering here when you have real data
        e.g. calculating tx_frequency from transaction history
        """
        features = []
        for feature in FEATURES:
            value = transaction.get(feature, 0)
            features.append(float(value))
        return np.array(features).reshape(1, -1)

    def _reconstruction_error(self, features_scaled: np.ndarray) -> float:
        """
        Runs the transaction through the autoencoder and
        returns the MSE reconstruction error.
        """
        with torch.no_grad():
            tensor = torch.FloatTensor(features_scaled)
            output = self.model(tensor)
            error = torch.mean((output - tensor) ** 2).item()
        return error

    def _normalize_score(self, error: float) -> float:
        """
        Converts raw reconstruction error to a 0-100 risk score.
        We use 10x the threshold as the upper bound so there is
        more breathing room between normal and anomalous scores.
        """
        # use 10x threshold as the upper bound for scaling
        upper_bound = self.threshold * 10
        score = (error / upper_bound) * 100
        return round(min(max(score, 0.0), 100.0), 2)

    def score(self, transaction: dict) -> dict:
        """
        Main method — takes a transaction dict and returns a risk assessment.
        
        Input example:
        {
            "amount": 0.5,
            "token_type": 0,
            "hour": 14,
            "day_of_week": 2,
            "gas_fee": 0.002,
            "is_new_address": 0,
            "time_since_last_tx": 3600,
            "tx_frequency": 2
        }

        Output example:
        {
            "risk_score": 12.5,
            "label": "normal",
            "reconstruction_error": 0.021,
            "threshold": 0.074712,
            "features_used": {...}
        }
        """
        # Step 1: extract features
        features = self._extract_features(transaction)

        # Step 2: normalize using saved scaler
        features_scaled = self.scaler.transform(features)

        # Step 3: get reconstruction error
        error = self._reconstruction_error(features_scaled)

        # Step 4: convert to 0-100 score
        risk_score = self._normalize_score(error)

        # Step 5: determine label
        if risk_score <= 30:
            label = "normal"
        elif risk_score <= 70:
            label = "suspicious"
        else:
            label = "anomalous"

        return {
            "risk_score":           risk_score,
            "label":                label,
            "reconstruction_error": round(error, 6),
            "threshold":            round(self.threshold, 6),
            "features_used":        transaction,
        }


# ── Quick test ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    scorer = AnomalyScorer()

    print("\n── Test 1: Normal Transaction ───────────────────────")
    normal_tx = {
        "amount":             0.5,
        "token_type":         0,
        "hour":               14,
        "day_of_week":        2,
        "gas_fee":            0.002,
        "is_new_address":     0,
        "time_since_last_tx": 3600,
        "tx_frequency":       2,
    }
    result = scorer.score(normal_tx)
    print(f"Risk Score:  {result['risk_score']}")
    print(f"Label:       {result['label']}")
    print(f"Recon Error: {result['reconstruction_error']}")

    print("\n── Test 2: Anomalous Transaction ────────────────────")
    anomalous_tx = {
        "amount":             45.0,
        "token_type":         0,
        "hour":               3,
        "day_of_week":        1,
        "gas_fee":            0.09,
        "is_new_address":     1,
        "time_since_last_tx": 10,
        "tx_frequency":       35,
    }
    result = scorer.score(anomalous_tx)
    print(f"Risk Score:  {result['risk_score']}")
    print(f"Label:       {result['label']}")
    print(f"Recon Error: {result['reconstruction_error']}")

    print("\n── Test 3: Borderline Transaction ───────────────────")
    borderline_tx = {
        "amount":             3.5,
        "token_type":         0,
        "hour":               8,
        "day_of_week":        5,
        "gas_fee":            0.008,
        "is_new_address":     0,
        "time_since_last_tx": 600,
        "tx_frequency":       6,
    }
    result = scorer.score(borderline_tx)
    print(f"Risk Score:  {result['risk_score']}")
    print(f"Label:       {result['label']}")
    print(f"Recon Error: {result['reconstruction_error']}")