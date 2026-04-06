# Backend/model/train.py

import torch
import torch.nn as nn
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pickle
import os

from torch.utils.data import DataLoader, TensorDataset
from sklearn.preprocessing import MinMaxScaler
from autoencoder import Autoencoder

# ── Hyperparameters ────────────────────────────────────────────────────────────
# These are settings you can tune to improve the model
# TODO: experiment with these values to see how they affect training
INPUT_DIM   = 8        # number of features per transaction
BATCH_SIZE  = 32       # number of transactions per training step
EPOCHS      = 100      # how many times to loop through the full dataset
LEARNING_RATE = 0.001  # how big each weight update step is
# ──────────────────────────────────────────────────────────────────────────────

def load_data(path: str = "../data/transactions.csv"):
    """
    Loads the transaction CSV and returns only the normal transactions.
    We train ONLY on normal data so the model never learns
    to reconstruct anomalies.
    """
    df = pd.read_csv(path)

    print(f"Total transactions loaded:    {len(df)}")
    print(f"Normal transactions:          {len(df[df['label'] == 0])}")
    print(f"Anomalous transactions:       {len(df[df['label'] == 1])}")

    # separate features from labels
    features = ["amount", "token_type", "hour", "day_of_week",
                "gas_fee", "is_new_address", "time_since_last_tx", "tx_frequency"]

    # keep only normal transactions for training
    normal_df = df[df["label"] == 0][features]
    all_df    = df[features]  # keep all for threshold calculation later

    return normal_df.values, all_df.values, df["label"].values


def normalize_data(normal_data: np.ndarray, all_data: np.ndarray):
    """
    Scales all features to range [0, 1] using MinMaxScaler.
    We fit the scaler on normal data only, then apply it to all data.
    We save the scaler so we can apply the same transformation
    to new transactions at inference time.
    """
    scaler = MinMaxScaler()

    # fit on normal data only
    normal_scaled = scaler.fit_transform(normal_data)
    all_scaled    = scaler.transform(all_data)

    # save scaler for inference
    os.makedirs("../data", exist_ok=True)
    with open("../data/scaler.pkl", "wb") as f:
        pickle.dump(scaler, f)
    print("Scaler saved to data/scaler.pkl")

    return normal_scaled, all_scaled


def create_dataloader(data: np.ndarray, batch_size: int) -> DataLoader:
    """
    Converts numpy array to PyTorch tensors and wraps in a DataLoader.
    DataLoader handles batching and shuffling automatically.
    """
    tensor = torch.FloatTensor(data)
    dataset = TensorDataset(tensor)
    return DataLoader(dataset, batch_size=batch_size, shuffle=True)


def train(model: Autoencoder,
          dataloader: DataLoader,
          epochs: int,
          learning_rate: float) -> list:
    """
    The main training loop.
    Trains the autoencoder on normal transactions only.
    Returns a list of loss values for plotting.
    """
    # MSE loss — measures reconstruction error
    criterion = nn.MSELoss()

    # Adam optimizer — adjusts weights to minimize loss
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

    losses = []

    print("\n── Training ─────────────────────────────────────────")
    for epoch in range(epochs):
        epoch_loss = 0.0
        num_batches = 0

        for batch in dataloader:
            # batch is a list with one element (the tensor)
            x = batch[0]

            # ── Core training step ─────────────────────────────
            optimizer.zero_grad()        # clear old gradients
            output = model(x)            # forward pass
            loss = criterion(output, x)  # compare reconstruction to input
            loss.backward()              # backpropagation
            optimizer.step()             # update weights
            # ──────────────────────────────────────────────────

            epoch_loss += loss.item()
            num_batches += 1

        avg_loss = epoch_loss / num_batches
        losses.append(avg_loss)

        # print progress every 10 epochs
        if (epoch + 1) % 10 == 0:
            print(f"Epoch [{epoch+1:3d}/{epochs}]  Loss: {avg_loss:.6f}")

    return losses


def calculate_threshold(model: Autoencoder,
                        all_scaled: np.ndarray,
                        labels: np.ndarray) -> float:
    """
    Calculates the anomaly threshold.
    We run all transactions through the model and look at the
    distribution of reconstruction errors on normal transactions.
    We set the threshold at the 95th percentile of normal errors —
    meaning only the top 5% most unusual normal transactions get flagged.
    TODO: tune this percentile based on how sensitive you want the detector
    """
    model.eval()  # set model to evaluation mode — disables dropout etc.

    with torch.no_grad():  # don't calculate gradients during inference
        tensor = torch.FloatTensor(all_scaled)
        outputs = model(tensor)
        # calculate MSE for each transaction individually
        errors = torch.mean((outputs - tensor) ** 2, dim=1).numpy()

    # get errors for normal transactions only
    normal_errors = errors[labels == 0]

    # 95th percentile of normal errors
    threshold = float(np.percentile(normal_errors, 95))

    print(f"\n── Threshold Calculation ────────────────────────────")
    print(f"Normal error   — mean: {normal_errors.mean():.6f}  std: {normal_errors.std():.6f}")
    print(f"Anomaly threshold set at 95th percentile: {threshold:.6f}")

    return threshold


def plot_loss(losses: list):
    """
    Plots the training loss over epochs so you can see
    if the model is learning correctly.
    A good training curve should decrease and level off.
    """
    plt.figure(figsize=(10, 4))
    plt.plot(losses)
    plt.title("Training Loss over Epochs")
    plt.xlabel("Epoch")
    plt.ylabel("MSE Loss")
    plt.grid(True)
    os.makedirs("../data", exist_ok=True)
    plt.savefig("../data/training_loss.png")
    print("Training loss plot saved to data/training_loss.png")
    plt.show()


def save_model(model: Autoencoder,
               threshold: float,
               path: str = "../data/saved_model.pth"):
    """
    Saves the trained model weights and threshold.
    We save both together so the scorer always uses
    the threshold that matches this specific model.
    """
    torch.save({
        "model_state_dict": model.state_dict(),
        "threshold":        threshold,
        "input_dim":        INPUT_DIM,
    }, path)
    print(f"Model saved to {path}")


if __name__ == "__main__":
    # ── Step 1: Load data ──────────────────────────────────────────────────
    print("── Loading Data ─────────────────────────────────────")
    normal_data, all_data, labels = load_data()

    # ── Step 2: Normalize ─────────────────────────────────────────────────
    print("\n── Normalizing Data ─────────────────────────────────")
    normal_scaled, all_scaled = normalize_data(normal_data, all_data)
    print(f"Normal data shape:  {normal_scaled.shape}")
    print(f"All data shape:     {all_scaled.shape}")

    # ── Step 3: Create DataLoader ──────────────────────────────────────────
    dataloader = create_dataloader(normal_scaled, BATCH_SIZE)
    print(f"Batches per epoch:  {len(dataloader)}")

    # ── Step 4: Create model ───────────────────────────────────────────────
    model = Autoencoder(input_dim=INPUT_DIM)
    print(f"\n── Model created with {sum(p.numel() for p in model.parameters())} parameters")

    # ── Step 5: Train ──────────────────────────────────────────────────────
    losses = train(model, dataloader, EPOCHS, LEARNING_RATE)

    # ── Step 6: Calculate threshold ────────────────────────────────────────
    threshold = calculate_threshold(model, all_scaled, labels)

    # ── Step 7: Plot loss ──────────────────────────────────────────────────
    plot_loss(losses)

    # ── Step 8: Save model ─────────────────────────────────────────────────
    save_model(model, threshold)

    print("\n✓ Training complete")