# Backend/model/train.py

import torch
import torch.nn as nn
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pickle
import os
from dotenv import load_dotenv

# Load env vars
load_dotenv()

from torch.utils.data import DataLoader, TensorDataset
from sklearn.preprocessing import MinMaxScaler
from autoencoder import Autoencoder

# -- Hyperparameters --
INPUT_DIM   = 8
BATCH_SIZE  = 32
EPOCHS      = 100
LEARNING_RATE = 0.001

def load_data():
    """
    Loads moving between synthetic and real data via env vars.
    """
    use_real = os.getenv("USE_REAL_DATA", "False").lower() == "true"
    default_path = "../data/transactions_real.csv" if use_real else "../data/transactions.csv"
    path = os.getenv("DATA_PATH", default_path)
    
    if not os.path.isabs(path):
        path = os.path.join(os.path.dirname(__file__), path)

    print(f"Loading data from: {path}")
    df = pd.read_csv(path)

    print(f"Total transactions loaded:    {len(df)}")
    print(f"Normal txs: {len(df[df['label'] == 0])}")
    print(f"Anomalous txs: {len(df[df['label'] == 1])}")

    features = ["amount", "token_type", "hour", "day_of_week",
                "gas_fee", "is_new_address", "time_since_last_tx", "tx_frequency"]

    normal_df = df[df["label"] == 0][features]
    all_df    = df[features]

    return normal_df.values, all_df.values, df["label"].values

def normalize_data(normal_data, all_data):
    scaler = MinMaxScaler()
    normal_scaled = scaler.fit_transform(normal_data)
    all_scaled    = scaler.transform(all_data)

    os.makedirs("../data", exist_ok=True)
    with open("../data/scaler.pkl", "wb") as f:
        pickle.dump(scaler, f)
    print("Scaler saved to data/scaler.pkl")

    return normal_scaled, all_scaled

def create_dataloader(data, batch_size):
    tensor = torch.FloatTensor(data)
    dataset = TensorDataset(tensor)
    return DataLoader(dataset, batch_size=batch_size, shuffle=True)

def train(model, dataloader, epochs, learning_rate):
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    losses = []

    print("\nTraining...")
    for epoch in range(epochs):
        epoch_loss = 0.0
        num_batches = 0
        for batch in dataloader:
            x = batch[0]
            optimizer.zero_grad()
            output = model(x)
            loss = criterion(output, x)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()
            num_batches += 1
        avg_loss = epoch_loss / num_batches
        losses.append(avg_loss)
        if (epoch + 1) % 10 == 0:
            print(f"Epoch [{epoch+1:3d}/{epochs}]  Loss: {avg_loss:.6f}")
    return losses

def calculate_threshold(model, all_scaled, labels):
    model.eval()
    with torch.no_grad():
        tensor = torch.FloatTensor(all_scaled)
        outputs = model(tensor)
        errors = torch.mean((outputs - tensor) ** 2, dim=1).numpy()

    normal_errors = errors[labels == 0]
    threshold = float(np.percentile(normal_errors, 95))

    print(f"\nThreshold Calculation")
    print(f"Normal error - mean: {normal_errors.mean():.6f}")
    print(f"Anomaly threshold set at 95th percentile: {threshold:.6f}")
    return threshold

def plot_loss(losses):
    plt.figure(figsize=(10, 4))
    plt.plot(losses)
    plt.savefig("../data/training_loss.png")
    print("Training loss plot saved to data/training_loss.png")

def save_model(model, threshold, path="../data/saved_model.pth"):
    torch.save({
        "model_state_dict": model.state_dict(),
        "threshold":        threshold,
        "input_dim":        INPUT_DIM,
    }, path)
    print(f"Model saved to {path}")

if __name__ == "__main__":
    normal_data, all_data, labels = load_data()
    normal_scaled, all_scaled = normalize_data(normal_data, all_data)
    dataloader = create_dataloader(normal_scaled, BATCH_SIZE)
    model = Autoencoder(input_dim=INPUT_DIM)
    losses = train(model, dataloader, EPOCHS, LEARNING_RATE)
    threshold = calculate_threshold(model, all_scaled, labels)
    save_model(model, threshold)
    print("\nSuccess: Training complete")
