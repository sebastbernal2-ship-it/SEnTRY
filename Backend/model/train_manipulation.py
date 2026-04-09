import numpy as np
import pandas as pd
import pickle
import os
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

def generate_synthetic_agents(n_samples=500):
    """
    Generates synthetic behavior data for 'Good' and 'Bad' agents.
    Features: [frequency, avg_size, success_rate, volatility]
    """
    np.random.seed(42)
    
    # Good Agents (Label 0)
    good_freq = np.random.uniform(1, 5, n_samples // 2)
    good_size = np.random.uniform(0.1, 2.0, n_samples // 2)
    good_success = np.random.uniform(0.8, 1.0, n_samples // 2)
    good_vol = np.random.uniform(0.01, 0.5, n_samples // 2)
    
    good_data = np.column_stack([good_freq, good_size, good_success, good_vol])
    good_labels = np.zeros(n_samples // 2)
    
    # Bad Agents (Label 1) - High frequency, high size, low success, high vol
    bad_freq = np.random.uniform(10, 50, n_samples // 2)
    bad_size = np.random.uniform(5.0, 50.0, n_samples // 2)
    bad_success = np.random.uniform(0.1, 0.4, n_samples // 2)
    bad_vol = np.random.uniform(2.0, 10.0, n_samples // 2)
    
    bad_data = np.column_stack([bad_freq, bad_size, bad_success, bad_vol])
    bad_labels = np.ones(n_samples // 2)
    
    X = np.vstack([good_data, bad_data])
    y = np.concatenate([good_labels, bad_labels])
    
    # Shuffle
    idx = np.random.permutation(len(X))
    return X[idx], y[idx]

def train_and_save():
    print("Generating synthetic agent data...")
    X, y = generate_synthetic_agents()
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    print("Training Logistic Regression model...")
    model = LogisticRegression()
    model.fit(X_train_scaled, y_train)
    
    accuracy = model.score(X_test_scaled, y_test)
    print(f"Model Accuracy: {accuracy:.4f}")
    
    # Save artifacts
    os.makedirs("../data", exist_ok=True)
    with open("../data/manipulation_model.pkl", "wb") as f:
        pickle.dump(model, f)
    with open("../data/manipulation_scaler.pkl", "wb") as f:
        pickle.dump(scaler, f)
    
    # Save a CSV for reference
    df = pd.DataFrame(X, columns=["frequency", "avg_size", "success_rate", "volatility"])
    df["label"] = y
    df.to_csv("../data/manipulation_train.csv", index=False)
    
    print("Success: Model saved to data/manipulation_model.pkl")

if __name__ == "__main__":
    train_and_save()
