import numpy as np
import pandas as pd
import pickle
import os
import time
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from xgboost import XGBClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score

def generate_synthetic_agents(n_samples=500):
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
    
    idx = np.random.permutation(len(X))
    return X[idx], y[idx]

class SimpleMLP(nn.Module):
    def __init__(self, input_dim=4):
        super(SimpleMLP, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 16),
            nn.ReLU(),
            nn.Linear(16, 8),
            nn.ReLU(),
            nn.Linear(8, 1),
            nn.Sigmoid()
        )
        
    def forward(self, x):
        return self.net(x)

def evaluate_model(model, X_test, y_test, is_pytorch=False):
    start_time = time.time()
    if is_pytorch:
        model.eval()
        with torch.no_grad():
            X_tensor = torch.FloatTensor(X_test)
            preds_prob = model(X_tensor).numpy().flatten()
            preds = (preds_prob > 0.5).astype(int)
    else:
        preds = model.predict(X_test)
    
    latency = (time.time() - start_time) / len(X_test) * 1000 # ms per sample
    
    acc = accuracy_score(y_test, preds)
    f1 = f1_score(y_test, preds)
    return acc, f1, latency

def train_pytorch_mlp(X_train, y_train, epochs=150):
    model = SimpleMLP()
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.01)
    
    X_tensor = torch.FloatTensor(X_train)
    y_tensor = torch.FloatTensor(y_train).view(-1, 1)
    
    for epoch in range(epochs):
        optimizer.zero_grad()
        outputs = model(X_tensor)
        loss = criterion(outputs, y_tensor)
        loss.backward()
        optimizer.step()
        
    return model

def train_and_save():
    print("Generating synthetic agent data...")
    X, y = generate_synthetic_agents(2000)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    models = {
        "Logistic Regression": LogisticRegression(),
        "Random Forest": RandomForestClassifier(n_estimators=50, random_state=42),
        "Gradient Boosting": GradientBoostingClassifier(n_estimators=50, random_state=42),
        "XGBoost": XGBClassifier(n_estimators=50, max_depth=3, random_state=42, eval_metric='logloss'),
        "PyTorch MLP": None
    }
    
    results = []
    trained_models = {}
    
    for name, model in models.items():
        if name == "PyTorch MLP":
            print(f"Training {name}...")
            trained_model = train_pytorch_mlp(X_train_scaled, y_train)
            trained_models[name] = trained_model
            acc, f1, lat = evaluate_model(trained_model, X_test_scaled, y_test, is_pytorch=True)
            results.append({"Model": name, "Accuracy": acc, "F1": f1, "Latency (ms)": lat})
        else:
            print(f"Training {name}...")
            model.fit(X_train_scaled, y_train)
            trained_models[name] = model
            acc, f1, lat = evaluate_model(model, X_test_scaled, y_test, is_pytorch=False)
            results.append({"Model": name, "Accuracy": acc, "F1": f1, "Latency (ms)": lat})
            
    print("\n--- Benchmark Results ---")
    df_results = pd.DataFrame(results)
    print(df_results.to_string(index=False))
    
    best_row = df_results.sort_values(by=["F1", "Latency (ms)"], ascending=[False, True]).iloc[0]
    best_name = best_row["Model"]
    
    print(f"\nWinning Architecture: {best_name}")
    
    os.makedirs("../data", exist_ok=True)
    with open("../data/manipulation_scaler.pkl", "wb") as f:
        pickle.dump(scaler, f)
        
    best_model = trained_models[best_name]
    
    if best_name == "PyTorch MLP":
        with open("../data/manipulation_model_type.txt", "w") as f:
            f.write("pytorch")
        torch.save(best_model.state_dict(), "../data/manipulation_model.pth")
    else:
        with open("../data/manipulation_model_type.txt", "w") as f:
            f.write("sklearn")
        with open("../data/manipulation_model.pkl", "wb") as f:
            pickle.dump(best_model, f)
            
    df = pd.DataFrame(X, columns=["frequency", "avg_size", "success_rate", "volatility"])
    df["label"] = y
    df.to_csv("../data/manipulation_train.csv", index=False)
    print("Success: Winning model and scaler saved!")

if __name__ == "__main__":
    train_and_save()
