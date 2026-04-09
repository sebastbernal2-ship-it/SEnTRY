import os
import pickle
import pandas as pd
import numpy as np

class ManipulationScorer:
    def __init__(self):
        self.model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/manipulation_model.pkl"))
        self.scaler_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/manipulation_scaler.pkl"))
        self.history_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/manipulation_history.csv"))
        
        self.model = None
        self.scaler = None
        
        if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
            with open(self.model_path, "rb") as f:
                self.model = pickle.load(f)
            with open(self.scaler_path, "rb") as f:
                self.scaler = pickle.load(f)
        else:
            raise FileNotFoundError("Manipulation model or scaler not found. Run train_manipulation.py first.")
            
        self.history = self._load_history()

    def _load_history(self):
        if os.path.exists(self.history_path):
            return pd.read_csv(self.history_path).set_index("agent_id").to_dict("index")
        return {}

    def _save_history(self):
        if self.history:
            df = pd.DataFrame.from_dict(self.history, orient="index")
            df.index.name = "agent_id"
            df.to_csv(self.history_path)

    def log_proposal(self, agent_id: str, size: float, success: bool):
        if agent_id not in self.history:
            self.history[agent_id] = {
                "total_proposals": 0,
                "successful_proposals": 0,
                "total_size": 0.0,
                "sum_sq_size": 0.0
            }
        
        agent = self.history[agent_id]
        agent["total_proposals"] += 1
        agent["total_size"] += size
        agent["sum_sq_size"] += size * size
        if success:
            agent["successful_proposals"] += 1
            
        self._save_history()

    def _get_features(self, agent_id: str):
        if agent_id not in self.history:
            return [1.0, 1.0, 1.0, 0.1] # Default safe fallback
            
        agent = self.history[agent_id]
        n = agent["total_proposals"]
        if n == 0:
            return [0.0, 0.0, 0.0, 0.0]
            
        # Mocking frequency as total proposals for demo simulation
        frequency = n 
        avg_size = agent["total_size"] / n
        success_rate = agent["successful_proposals"] / n
        
        # calculate variance
        mean = avg_size
        variance = (agent["sum_sq_size"] / n) - (mean * mean)
        if variance < 0: 
            variance = 0
            
        volatility = np.sqrt(variance)
        
        return [frequency, avg_size, success_rate, volatility]

    def score_agent(self, agent_id: str):
        if not self.model or not self.scaler:
            return {"risk_score": 0, "label": "error", "message": "Model not loaded", "agent_id": agent_id}
            
        features = self._get_features(agent_id)
        
        # Scale features
        # Reshape to 2D array
        features_array = np.array(features).reshape(1, -1)
        scaled_features = self.scaler.transform(features_array)
        
        # Predict probability of class 1 (bad agent)
        prob = self.model.predict_proba(scaled_features)[0][1]
        
        # Convert to 0-100 score
        risk_score = round(prob * 100, 2)
        
        # Determine label based on SENTRY thresholds
        if risk_score > 70:
            label = "blocked"
        elif risk_score > 30:
            label = "flagged"
        else:
            label = "safe"
            
        return {
            "agent_id": agent_id,
            "risk_score": risk_score,
            "label": label,
            "metrics": {
                "frequency": round(features[0], 2),
                "avg_size": round(features[1], 2),
                "success_rate": round(features[2], 2),
                "volatility": round(features[3], 2)
            }
        }

    def get_all_agents(self):
        results = []
        for agent_id in self.history.keys():
            results.append(self.score_agent(agent_id))
        return results
