import joblib
import os
import pandas as pd
import warnings

# Suppress sklearn warnings for missing feature names during inference 
warnings.filterwarnings("ignore", category=UserWarning)

MODEL_PATH = os.path.join(os.path.dirname(__file__), "rf_classifier.pkl")
_model = None

def load_model():
    global _model
    if os.path.exists(MODEL_PATH):
        try:
            _model = joblib.load(MODEL_PATH)
        except Exception as e:
            print(f"Failed to load ML classifier: {e}")
            _model = None

def predict(snapshot) -> str:
    """
    Returns the ML model prediction ('benign', 'suspicious', 'manual_review').
    Falls back to None if the model is untrained/unavailable.
    """
    global _model
    if not _model:
        load_model()
        
    if not _model:
        return "N/A (Untrained)"

    try:
        df = pd.DataFrame([{
            "interaction_count": snapshot.interaction_count or 0,
            "success_rate": snapshot.success_rate or 0,
            "mean_size": snapshot.mean_size or 0,
            "size_std": snapshot.size_std or 0,
            "unique_destinations": snapshot.unique_destinations or 0,
            "destination_concentration": snapshot.destination_concentration or 0,
            "frequency_spike_score": snapshot.frequency_spike_score or 0,
            "size_spike_score": snapshot.size_spike_score or 0
        }])
        
        return _model.predict(df)[0]
    except Exception as e:
        print(f"ML Inference error: {e}")
        return "N/A (Error)"
