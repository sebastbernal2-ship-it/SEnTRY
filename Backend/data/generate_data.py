# Backend/data/generate_data.py

import pandas as pd
import numpy as np
import random
import os

np.random.seed(42)
random.seed(42)

# ── Known addresses your agent normally interacts with ────────────────────────
# TODO: Replace these with your agent's actual known addresses
KNOWN_ADDRESSES = [
    "0xaB3f...221C",
    "0x9f2A...88BD",
    "0x1122...AABB",
    "0x5544...33CC",
    "0x7788...DDEE",
    "0xAABB...1234",
    "0xCCDD...5678",
    "0xEEFF...9ABC",
]

# ── Token encoding ────────────────────────────────────────────────────────────
# TODO: Add more tokens your agent uses
TOKEN_MAP = {
    "ETH":  0,
    "USDC": 1,
    "WBTC": 2,
    "DAI":  3,
}

def generate_normal_transaction() -> dict:
    """
    Generates a single normal transaction that reflects
    typical behavior of your agent.
    Normal characteristics:
    - Small to medium amounts (0.1 - 2 ETH equivalent)
    - Business hours (9am - 6pm)
    - Known destination addresses
    - Low gas fees
    - Regular frequency
    """
    return {
        "amount":             round(np.random.uniform(0.1, 2.0), 4),
        "token_type":         random.choice(list(TOKEN_MAP.values())),
        "hour":               int(np.random.uniform(9, 18)),
        "day_of_week":        random.randint(0, 6),
        "gas_fee":            round(np.random.uniform(0.001, 0.005), 6),
        "is_new_address":     0,
        "time_since_last_tx": int(np.random.uniform(300, 7200)),  # 5min to 2hrs in seconds
        "tx_frequency":       random.randint(1, 5),               # txs in last hour
        "label":              0                                    # 0 = normal
    }


def generate_anomalous_transaction() -> dict:
    """
    Generates a single anomalous transaction.
    Starts with a normal transaction and corrupts one or more features
    to simulate different types of attacks or manipulation.
    Anomaly types:
    - large_amount:  sudden huge transfer
    - odd_hour:      trading at suspicious hours
    - new_address:   sending to unknown destination
    - high_gas:      unusually high gas (urgency signal)
    - burst:         too many transactions too fast
    - combined:      multiple anomaly signals at once (worst case)
    """
    anomaly_type = random.choice([
        "large_amount",
        "odd_hour",
        "new_address",
        "high_gas",
        "burst",
        "combined",
    ])

    # start from a normal transaction and corrupt it
    tx = generate_normal_transaction()
    tx["label"] = 1  # 1 = anomalous

    if anomaly_type == "large_amount":
        # sudden large swap — 10x to 25x normal amount
        tx["amount"] = round(np.random.uniform(20.0, 50.0), 4)

    elif anomaly_type == "odd_hour":
        # trading at 12am - 4am
        tx["hour"] = random.choice([0, 1, 2, 3, 4])

    elif anomaly_type == "new_address":
        # sending to a brand new unknown address
        tx["is_new_address"] = 1
        tx["amount"] = round(np.random.uniform(5.0, 15.0), 4)

    elif anomaly_type == "high_gas":
        # high gas fee signals urgency / manipulation
        tx["gas_fee"] = round(np.random.uniform(0.05, 0.15), 6)

    elif anomaly_type == "burst":
        # too many transactions in a very short window
        tx["tx_frequency"]       = random.randint(20, 50)
        tx["time_since_last_tx"] = random.randint(1, 30)  # seconds apart

    elif anomaly_type == "combined":
        # multiple red flags at once — the most suspicious
        tx["amount"]             = round(np.random.uniform(15.0, 40.0), 4)
        tx["hour"]               = random.choice([1, 2, 3])
        tx["is_new_address"]     = 1
        tx["gas_fee"]            = round(np.random.uniform(0.04, 0.1), 6)
        tx["tx_frequency"]       = random.randint(15, 30)
        tx["time_since_last_tx"] = random.randint(5, 60)

    return tx


def generate_dataset(
    n_normal: int = 1000,
    n_anomalous: int = 50,
) -> pd.DataFrame:
    """
    Generates a full dataset of normal and anomalous transactions.
    We use far more normal than anomalous transactions because:
    1. This reflects reality — most transactions are normal
    2. The autoencoder trains ONLY on normal data anyway
    3. The anomalous ones are just for testing/evaluation later
    """
    print(f"Generating {n_normal} normal transactions...")
    normal_txs = [generate_normal_transaction() for _ in range(n_normal)]

    print(f"Generating {n_anomalous} anomalous transactions...")
    anomalous_txs = [generate_anomalous_transaction() for _ in range(n_anomalous)]

    all_txs = normal_txs + anomalous_txs
    random.shuffle(all_txs)

    df = pd.DataFrame(all_txs)
    return df


def save_dataset(df: pd.DataFrame, path: str = "data/transactions.csv"):
    """
    Saves the dataset to a CSV file.
    Creates the data/ directory if it doesn't exist.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)
    print(f"Saved {len(df)} transactions to {path}")


def print_summary(df: pd.DataFrame):
    """
    Prints a summary of the generated dataset
    so you can sanity check it looks right.
    """
    print("\n── Dataset Summary ──────────────────────────────")
    print(f"Total transactions:    {len(df)}")
    print(f"Normal transactions:   {len(df[df['label'] == 0])}")
    print(f"Anomalous transactions:{len(df[df['label'] == 1])}")
    print("\n── Feature Ranges ───────────────────────────────")
    print(df.drop(columns=["label"]).describe().round(4))
    print("\n── Sample Normal Transaction ────────────────────")
    print(df[df["label"] == 0].iloc[0].to_dict())
    print("\n── Sample Anomalous Transaction ─────────────────")
    print(df[df["label"] == 1].iloc[0].to_dict())


if __name__ == "__main__":
    df = generate_dataset(n_normal=1000, n_anomalous=50)
    save_dataset(df)
    print_summary(df)