"""
Transaction Anomaly Detection Module
Uses PyTorch Autoencoder for behavioral pattern detection.
"""
import os
import sys
import pickle
import importlib
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

            if not self._is_valid_model_file(MODEL_PATH):
                print("[Anomaly] Invalid model artifact payload; using heuristic fallback scoring.")
                self.model = None
                self.scaler = None
                self.use_model = False
                return

            if not self._is_valid_scaler_file(SCALER_PATH):
                print("[Anomaly] Invalid scaler artifact payload; using heuristic fallback scoring.")
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
            
            # Load scaler with compatibility fallback for older pickle module paths.
            self.scaler = self._load_scaler_with_compat(SCALER_PATH)
            
            print(f"[Anomaly] Model loaded - threshold: {self.threshold:.6f}")
        except Exception as e:
            print(f"[Anomaly] Failed to load model: {e}")
            self.model = None
            self.scaler = None
            self.use_model = False

    @staticmethod
    def _looks_like_text_payload(header: bytes) -> bool:
        """Detect HTML/LFS/text payloads that indicate a bad artifact download."""
        lowered = header.lower()
        return (
            lowered.startswith(b"<!doctype")
            or lowered.startswith(b"<html")
            or b"github" in lowered and b"not found" in lowered
            or lowered.startswith(b"version https://git-lfs.github.com/spec")
        )

    @classmethod
    def _is_valid_model_file(cls, path: str) -> bool:
        """Validate model file header before attempting torch.load."""
        try:
            with open(path, "rb") as f:
                header = f.read(256)
            if len(header) == 0:
                return False
            if cls._looks_like_text_payload(header):
                return False
            # torch.save often creates a zip archive (PK) or pickle stream (0x80)
            return header.startswith(b"PK") or header.startswith(b"\x80")
        except Exception:
            return False

    @classmethod
    def _is_valid_scaler_file(cls, path: str) -> bool:
        """Validate scaler pickle header before attempting pickle.load."""
        try:
            with open(path, "rb") as f:
                header = f.read(256)
            if len(header) == 0:
                return False
            if cls._looks_like_text_payload(header):
                return False
            return header.startswith(b"\x80")
        except Exception:
            return False

    @staticmethod
    def _load_scaler_with_compat(path: str):
        """Load scaler pickle with compatibility shim for numpy module path changes."""
        try:
            with open(path, 'rb') as f:
                return pickle.load(f)
        except ModuleNotFoundError as exc:
            if exc.name != "numpy._core":
                raise

            print("[Anomaly] Applying numpy._core compatibility shim for scaler load.")

            # Older pickles may reference numpy._core.* while this runtime exposes
            # numpy.core.*. Register aliases for both package and common submodules.
            numpy_core_pkg = importlib.import_module("numpy.core")
            numpy_core_multiarray = importlib.import_module("numpy.core.multiarray")
            numpy_core_numeric = importlib.import_module("numpy.core.numeric")

            sys.modules.setdefault("numpy._core", numpy_core_pkg)
            sys.modules.setdefault("numpy._core.multiarray", numpy_core_multiarray)
            sys.modules.setdefault("numpy._core.numeric", numpy_core_numeric)

            with open(path, 'rb') as f:
                return pickle.load(f)

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
        threshold = max(float(self.threshold), 1e-9)
        ratio = max(float(error), 0.0) / threshold
        # Smooth non-linear mapping to reduce saturation on out-of-distribution inputs.
        score = 100.0 * (1.0 - np.exp(-ratio / 3.0))
        return float(min(max(score, 0.0), 100.0))

    def _normalize_scores_batch(self, errors: np.ndarray) -> np.ndarray:
        """Convert reconstruction errors to calibrated 0-100 scores for a batch."""
        if errors.size == 0:
            return np.array([], dtype=float)

        threshold = max(float(self.threshold), 1e-9)
        ratios = np.maximum(errors, 0.0) / threshold

        if errors.size == 1:
            return np.array([self._normalize_score(float(errors[0]))], dtype=float)

        order = np.argsort(errors)
        ranks = np.empty_like(order, dtype=float)
        ranks[order] = np.arange(errors.size, dtype=float)
        percentile_component = (ranks / max(errors.size - 1, 1)) * 70.0

        # Add a gentler anomaly boost relative to model threshold. Using a
        # log curve prevents most real-wallet transactions from saturating.
        threshold_excess = np.maximum(ratios - 1.0, 0.0)
        threshold_boost = np.clip(np.log1p(threshold_excess) * 12.0, 0.0, 25.0)

        scores = np.clip(percentile_component + threshold_boost, 0.0, 100.0)
        return scores.astype(float)

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
            # Real-wallet values can exceed training ranges; clip to scaler
            # support to reduce out-of-distribution score inflation.
            features_scaled = np.clip(features_scaled, 0.0, 1.0)
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
        if not transactions:
            return []

        if not (self.use_model and self.model is not None and self.scaler is not None):
            return [self.score_transaction(tx) for tx in transactions]

        try:
            features = np.vstack([self._extract_features(tx) for tx in transactions])
            features_scaled = self.scaler.transform(features)
            features_scaled = np.clip(features_scaled, 0.0, 1.0)

            with torch.no_grad():
                tensor = torch.FloatTensor(features_scaled)
                outputs = self.model(tensor)
                errors = torch.mean((outputs - tensor) ** 2, dim=1).cpu().numpy()

            risk_scores = self._normalize_scores_batch(errors)

            results = []
            for tx, risk_score in zip(transactions, risk_scores):
                label = score_to_label(risk_score)
                severity = score_to_severity(risk_score)
                results.append({
                    "risk_score": round(float(risk_score), 2),
                    "label": label,
                    "severity": severity,
                    "features_used": list(tx.keys()),
                })
            return results
        except Exception as e:
            print(f"[Anomaly] Batch model scoring failed: {e}. Falling back to per-transaction scoring.")
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
