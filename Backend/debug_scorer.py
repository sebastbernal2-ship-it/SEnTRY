# debug_scorer.py
import sys
import os
import pandas as pd
import numpy as np

# Add api to path
sys.path.append(os.path.join(os.getcwd(), "api"))
from scorer import AnomalyScorer

def test_random_score():
    try:
        print("Initializing Scorer...")
        scorer = AnomalyScorer()
        
        path = "data/transactions_real.csv"
        print(f"Loading data from {path}...")
        df = pd.read_csv(path)
        
        sample = df.drop(columns=["label"]).sample(n=1).to_dict(orient="records")[0]
        print(f"Sample transaction: {sample}")
        
        print("Scoring...")
        result = scorer.score(sample)
        print(f"Result: {result}")
        
        # Test the formatting logic from main.py
        print("Testing formatting logic...")
        token = ["ETH", "USDC", "WBTC", "DAI"][int(sample["token_type"])]
        time_str = f"{int(sample['hour']):02d}:00"
        print(f"Formatted Token: {token}")
        print("Formatted Time: " + time_str)
        print("All logic passed!")
        
    except Exception as e:
        print(f"!!! Error caught: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_random_score()
