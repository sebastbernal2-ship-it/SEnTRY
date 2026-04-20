"""
Transaction Anomaly Detection Module
Uses PyTorch Autoencoder for behavioral pattern detection.
"""
import os
import sys
import pickle
import numpy as np
import torch
import random
from datetime import datetime, timezone
from typing import Dict, Any, List
from pathlib import Path

# Add Backend path to import Autoencoder
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../Backend'))
sys.path.insert(0, backend_path)

try:
    from model.autoencoder import Autoencoder
except ImportError:
    Autoencoder = None

from ..utils.scoring import (
    load_pytorch_model, load_scaler, score_to_label, normalize_score, score_to_severity
)
from ..utils.io import get_utc_now


MODEL_PATH = os.path.join(backend_path, 'data/saved_model.pth')
SCALER_PATH = os.path.join(backend_path, 'data/scaler.pkl')

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


class TransactionAnomalyDetector:
    """Detects anomalous transactions using PyTorch Autoencoder."""

    def __init__(self, use_model: bool = True):
        """
        Initialize detector.
        
        Args:
            use_model: If True, load actual model. If False, use fallback scoring.
        """
        self.use_model = use_model and Autoencoder is not None
        self.model = None
        self.scaler = None
        self.threshold = 0.005
        
        if self.use_model:
            self._load_model()

    def _load_model(self) -> None:
        """Load PyTorch model and scaler."""
        try:
            if not os.path.exists(MODEL_PATH) or not os.path.exists(SCALER_PATH):
                print("[Anomaly] Model artifacts not found; using heuristic fallback scoring.")
                self.model = None
                self.scaler = None
                self.use_model = False
                return

            print("[Anomaly] Loading PyTorch Autoencoder...")
            
            # Load checkpoint
            checkpoint = torch.load(MODEL_PATH, map_location='cpu')
            input_dim = checkpoint.get('input_dim', 8)
            self.threshold = checkpoint.get('threshold', 0.005)
            
            # Load model
            self.model = Autoencoder(input_dim=input_dim)
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.model.eval()
            
            # Load scaler
            with open(SCALER_PATH, 'rb') as f:
                self.scaler = pickle.load(f)
            
            print(f"[Anomaly] Model loaded - threshold: {self.threshold:.6f}")
        except Exception as e:
            print(f"[Anomaly] Failed to load model: {e}")
            self.model = None
            self.scaler = None
            self.use_model = False

    def _extract_features(self, transaction: Dict[str, Any]) -> np.ndarray:
        """Extract and order features for model input."""
        features = []
        for feature in FEATURES:
            value = transaction.get(feature, 0)
            features.append(float(value))
        return np.array(features).reshape(1, -1)

    def _reconstruction_error(self, features_scaled: np.ndarray) -> float:
        """Compute reconstruction error from autoencoder."""
        if self.model is None:
            return 0.0
        
        try:
            with torch.no_grad():
                tensor = torch.FloatTensor(features_scaled)
                output = self.model(tensor)
                error = torch.mean((output - tensor) ** 2).item()
            return error
        except Exception as e:
            print(f"[Anomaly] Reconstruction error: {e}")
            return 0.0

    def _normalize_score(self, error: float) -> float:
        """Convert reconstruction error to 0-100 risk score."""
        upper_bound = self.threshold * 10
        score = (error / upper_bound) * 100
        return float(min(max(score, 0.0), 100.0))

    def _fallback_score(self, transaction: Dict[str, Any]) -> float:
        """
        Deterministic fallback scoring when model unavailable.
        Uses simple heuristics based on transaction features.
        """
        score = 0.0
        
        # Large amounts increase risk
        amount = transaction.get('amount', 0)
        if amount > 10:
            score += 20
        elif amount > 5:
            score += 10
        
        # New addresses increase risk
        if transaction.get('is_new_address', 0) > 0.5:
            score += 15
        
        # High frequency increase risk
        freq = transaction.get('tx_frequency', 0)
        if freq > 10:
            score += 25
        elif freq > 5:
            score += 10
        
        # Off-hours slightly increase risk
        hour = transaction.get('hour', 12)
        if hour < 6 or hour > 22:
            score += 5
        
        return min(score, 100.0)

    def score_transaction(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Score a single transaction.
        
        Args:
            transaction: Transaction data dict
        
        Returns:
            Scoring result with score, label, etc.
        """
        if self.use_model and self.model is not None and self.scaler is not None:
            # Use model
            features = self._extract_features(transaction)
            features_scaled = self.scaler.transform(features)
            error = self._reconstruction_error(features_scaled)
            risk_score = self._normalize_score(error)
        else:
            # Use fallback
            risk_score = self._fallback_score(transaction)
        
        label = score_to_label(risk_score)
        severity = score_to_severity(risk_score)
        
        return {
            "risk_score": round(risk_score, 2),
            "label": label,
            "severity": severity,
            "features_used": list(transaction.keys()),
        }

    def score_batch(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Score multiple transactions."""
        return [self.score_transaction(tx) for tx in transactions]

    def generate_demo_transactions(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        Generate demo transaction data for testing.
        
        Args:
            count: Number of demo transactions
        
        Returns:
            List of demo transaction dicts
        """
        transactions = []
        for i in range(count):
            tx = {
                "id": f"tx-{i:04d}",
                "amount": round(random.uniform(0.1, 50), 2),
                "token_type": random.choice([0, 1, 2]),  # ETH, USDC, DAI
                "hour": random.randint(0, 23),
                "day_of_week": random.randint(0, 6),
                "gas_fee": round(random.uniform(5, 100), 2),
                "is_new_address": random.choice([0, 1]),
                "time_since_last_tx": random.randint(0, 1000),
                "tx_frequency": random.randint(0, 20),
            }
            transactions.append(tx)
        return transactions
