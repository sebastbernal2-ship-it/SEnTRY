"""
Common scoring functions and model loading utilities.
Handles PyTorch and scikit-learn inference.
"""
import os
import sys
import pickle
import numpy as np
import torch
from pathlib import Path
from typing import Dict, Any, Optional, Tuple


def get_backend_path() -> str:
    """Get absolute path to Backend directory."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, '../../Backend')


def load_pytorch_model(model_path: str, model_class):
    """
    Load a PyTorch model checkpoint.
    
    Args:
        model_path: Path to .pth file
        model_class: Model class to instantiate
    
    Returns:
        Loaded model in eval mode, or None if load fails
    """
    if not os.path.exists(model_path):
        print(f"Warning: Model file not found: {model_path}")
        return None
    
    try:
        checkpoint = torch.load(model_path, map_location='cpu')
        model = model_class(input_dim=checkpoint.get('input_dim', 8))
        model.load_state_dict(checkpoint['model_state_dict'])
        model.eval()
        return model
    except Exception as e:
        print(f"Error loading PyTorch model: {e}")
        return None


def load_sklearn_model(model_path: str):
    """
    Load a scikit-learn model from pickle.
    
    Args:
        model_path: Path to .pkl file
    
    Returns:
        Loaded model, or None if load fails
    """
    if not os.path.exists(model_path):
        print(f"Warning: Model file not found: {model_path}")
        return None
    
    try:
        with open(model_path, 'rb') as f:
            return pickle.load(f)
    except Exception as e:
        print(f"Error loading sklearn model: {e}")
        return None


def load_scaler(scaler_path: str):
    """
    Load a scikit-learn scaler (StandardScaler, etc.).
    
    Args:
        scaler_path: Path to .pkl file
    
    Returns:
        Loaded scaler, or None if load fails
    """
    if not os.path.exists(scaler_path):
        print(f"Warning: Scaler file not found: {scaler_path}")
        return None
    
    try:
        with open(scaler_path, 'rb') as f:
            return pickle.load(f)
    except Exception as e:
        print(f"Error loading scaler: {e}")
        return None


def score_to_label(score: float) -> str:
    """
    Convert numeric score (0-100) to label.
    
    Args:
        score: Risk score
    
    Returns:
        Label: 'Clean', 'Suspicious', 'High Risk', or 'Manipulative'
    """
    if score <= 30:
        return "Clean"
    elif score <= 70:
        return "Suspicious"
    else:
        return "High Risk"


def score_to_severity(score: float) -> str:
    """
    Convert numeric score to severity level.
    
    Args:
        score: Risk score
    
    Returns:
        Severity: 'low', 'medium', or 'high'
    """
    if score <= 30:
        return "low"
    elif score <= 70:
        return "medium"
    else:
        return "high"


def normalize_score(raw_value: float, min_val: float = 0, max_val: float = 100) -> float:
    """
    Normalize a raw score to 0-100 range.
    
    Args:
        raw_value: Raw score value
        min_val: Expected minimum
        max_val: Expected maximum
    
    Returns:
        Normalized score clamped to 0-100
    """
    if max_val == min_val:
        return 50.0
    
    normalized = ((raw_value - min_val) / (max_val - min_val)) * 100
    return float(max(min(normalized, 100.0), 0.0))
