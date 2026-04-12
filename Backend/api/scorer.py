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

# -- Paths --
MODEL_PATH  = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/saved_model.pth"))
SCALER_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/scaler.pkl"))

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

        # -- Load saved model --
        checkpoint = torch.load(MODEL_PATH, map_location="cpu")
        self.input_dim = checkpoint["input_dim"]
        self.threshold = checkpoint["threshold"]

        self.model = Autoencoder(input_dim=self.input_dim)
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.model.eval()  # set to evaluation mode

        # -- Load scaler --
        with open(SCALER_PATH, "rb") as f:
            self.scaler = pickle.load(f)

        print(f"Model loaded - anomaly threshold: {self.threshold:.6f}")

    def _extract_features(self, transaction: dict) -> np.ndarray:
        features = []
        for feature in FEATURES:
            value = transaction.get(feature, 0)
            features.append(float(value))
        return np.array(features).reshape(1, -1)

    def _reconstruction_error(self, features_scaled: np.ndarray) -> float:
        with torch.no_grad():
            tensor = torch.FloatTensor(features_scaled)
            output = self.model(tensor)
            error = torch.mean((output - tensor) ** 2).item()
        return error

    def _normalize_score(self, error: float) -> float:
        upper_bound = self.threshold * 10
        score = (error / upper_bound) * 100
        return round(min(max(score, 0.0), 100.0), 2)

    def score(self, transaction: dict) -> dict:
        features = self._extract_features(transaction)
        features_scaled = self.scaler.transform(features)
        error = self._reconstruction_error(features_scaled)
        risk_score = self._normalize_score(error)

        if risk_score <= 30:
            label = "Likely Benign"
        elif risk_score <= 70:
            label = "Suspicious"
        else:
            label = "Requires Manual Review"

        return {
            "risk_score":           risk_score,
            "label":                label,
            "reconstruction_error": round(error, 6),
            "threshold":            round(self.threshold, 6),
            "features_used":        transaction,
        }

if __name__ == "__main__":
    scorer = AnomalyScorer()
    print("--- Test Output ---")
    test_tx = {
        "amount": 0.5, "token_type": 0, "hour": 14, "day_of_week": 2,
        "gas_fee": 0.002, "is_new_address": 0, "time_since_last_tx": 3600, "tx_frequency": 2
    }
    print(scorer.score(test_tx))
