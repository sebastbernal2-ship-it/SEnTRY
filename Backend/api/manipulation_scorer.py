import os
import pickle
import pandas as pd
import numpy as np

MODEL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/manipulation_model.pkl"))
SCALER_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/manipulation_scaler.pkl"))
HISTORY_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/manipulation_history.csv"))

class ManipulationScorer:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.history = {}
        
        self.load_artifacts()
        self.load_history()

    def load_artifacts(self):
        if os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH):
            with open(MODEL_PATH, "rb") as f:
                self.model = pickle.load(f)
            with open(SCALER_PATH, "rb") as f:
                self.scaler = pickle.load(f)
            print("ManipulationScorer: Model and Scaler loaded successfully.")
        else:
            print("ManipulationScorer: Warning - Model artifacts not found. Call train_manipulation.py first.")

    def load_history(self):
        if os.path.exists(HISTORY_PATH):
            df = pd.read_csv(HISTORY_PATH)
            for _, row in df.iterrows():
                agent_id = row['agent_id']
                if agent_id not in self.history:
                    self.history[agent_id] = []
                # Keep a window of recent proposals
                self.history[agent_id].append({
                    "size": float(row["size"]),
                    "success": bool(row["success"])
                })
        else:
            # Create empty CSV
            pd.DataFrame(columns=["agent_id", "size", "success"]).to_csv(HISTORY_PATH, index=False)

    def log_proposal(self, agent_id: str, size: float, success: bool):
        # Update in-memory
        if agent_id not in self.history:
            self.history[agent_id] = []
            
        self.history[agent_id].append({"size": size, "success": success})
        
        # Keep only the last 100 to avoid runaway memory/time
        if len(self.history[agent_id]) > 100:
            self.history[agent_id] = self.history[agent_id][-100:]
            
        # Append to CSV
        new_row = pd.DataFrame([{"agent_id": agent_id, "size": size, "success": success}])
        new_row.to_csv(HISTORY_PATH, mode='a', header=False, index=False)

    def calculate_features(self, agent_id: str) -> dict:
        proposals = self.history.get(agent_id, [])
        if not proposals:
            return {"frequency": 0, "avg_size": 0, "success_rate": 1.0, "volatility": 0}
            
        freq = len(proposals)
        sizes = [p["size"] for p in proposals]
        successes = [1 if p["success"] else 0 for p in proposals]
        
        avg_size = np.mean(sizes) if sizes else 0
        success_rate = np.mean(successes) if successes else 1.0
        volatility = np.std(sizes) if len(sizes) > 1 else 0
        
        return {
            "frequency": freq,
            "avg_size": avg_size,
            "success_rate": success_rate,
            "volatility": volatility
        }

    def score_agent(self, agent_id: str) -> dict:
        features = self.calculate_features(agent_id)
        
        if not self.model or not self.scaler:
            return {"agent_id": agent_id, "risk_score": 0, "label": "Unknown (No Model)", "features": features}

        # Format input for typical sklearn models
        input_data = np.array([[
            features["frequency"], 
            features["avg_size"], 
            features["success_rate"], 
            features["volatility"]
        ]])
        
        # Standardize features
        input_scaled = self.scaler.transform(input_data)
        
        # Determine risk
        prob = self.model.predict_proba(input_scaled)[0][1] # Probability of Class 1 (Bad behavior)
        risk_score = round(prob * 100, 2)
        
        if risk_score <= 30:
            label = "Likely Benign"
        elif risk_score <= 70:
            label = "Suspicious"
        else:
            label = "Requires Manual Review"
            
        return {
            "agent_id": agent_id,
            "risk_score": risk_score,
            "label": label,
            "features": features
        }

    def get_all_agents(self) -> list:
        agents = []
        for agent_id in self.history.keys():
            agents.append(self.score_agent(agent_id))
        return agents
