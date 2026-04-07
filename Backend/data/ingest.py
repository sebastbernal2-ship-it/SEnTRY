# Backend/data/ingest.py

import os
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timezone
from dotenv import load_dotenv

# Load env vars
load_dotenv()

# Config
ALCHEMY_API_KEY = os.getenv("ALCHEMY_API_KEY")
TARGET_WALLET   = os.getenv("TARGET_WALLET_ADDRESS")
NETWORK         = os.getenv("ALCHEMY_NETWORK", "eth-mainnet")
ALCHEMY_URL     = f"https://{NETWORK}.g.alchemy.com/v2/{ALCHEMY_API_KEY}"

def fetch_eth_transfers(wallet_address):
    """
    Fetches native ETH transfers for the given wallet address using Alchemy.
    """
    payload = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "alchemy_getAssetTransfers",
        "params": [
            {
                "fromAddress": wallet_address,
                "category": ["external"], # only native ETH
                "withMetadata": True,
                "excludeZeroValue": False,
                "maxCount": "0x3e8" # Max 1000
            }
        ]
    }
    
    headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }

    print(f"Fetching history for: {wallet_address}...")
    response = requests.post(ALCHEMY_URL, json=payload, headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"Alchemy API error: {response.text}")
    
    result = response.json()
    if "result" not in result:
        raise Exception(f"Unexpected Alchemy response: {result}")
        
    return result["result"]["transfers"]

def process_transfers(transfers):
    """
    Transforms raw Alchemy transfers into the 8-feature schema.
    Features: amount, token_type, hour, day_of_week, gas_fee, 
              is_new_address, time_since_last_tx, tx_frequency
    """
    # Sort transfers chronologically by block number (and metadata timestamp)
    # Most likely already sorted but let's be safe
    transfers.sort(key=lambda x: int(x["blockNum"], 16))
    
    processed_data = []
    seen_destinations = set()
    last_tx_time = None
    
    print(f"Processing {len(transfers)} transactions...")

    for i, tx in enumerate(transfers):
        try:
            # 1. basic info
            value = float(tx["value"])
            to_addr = tx["to"].lower()
            
            # UTC Time extraction
            # Alchemy metadata time format: "2024-03-20T12:34:56.789Z"
            ts_str = tx["metadata"]["blockTimestamp"]
            dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
            current_ts = dt.timestamp()
            
            # ── 8-Feature Calculation ──
            
            # Feature 1: amount
            amount = value
            
            # Feature 2: token_type (0 for Native ETH)
            token_type = 0
            
            # Feature 3: hour (UTC)
            hour = dt.hour
            
            # Feature 4: day_of_week (UTC)
            day_of_week = dt.weekday()
            
            # Feature 5: gas_fee
            # Alchemy's getAssetTransfers doesn't include gas details directly.
            # For a student MVP, we'll use a fixed/estimated gas for V1 or
            # skip it if not critical for the "normal" behavior baseline.
            # TODO: Fetch transaction receipt for exact gasPrice * gasUsed
            gas_fee = 0.0005 # Placeholder for V1 to match schema
            
            # Feature 6: is_new_address
            # "1 if the destination to address has never previously appeared 
            # as a destination for this wallet in prior transactions"
            is_new_address = 1 if to_addr not in seen_destinations else 0
            seen_destinations.add(to_addr)
            
            # Feature 7: time_since_last_tx
            if last_tx_time is None:
                time_since_last_tx = 3600 # Default for first tx
            else:
                time_since_last_tx = int(current_ts - last_tx_time)
            last_tx_time = current_ts
            
            # Feature 8: tx_frequency (txs in last hour)
            # Simple window count on current history
            recent_tx_count = 0
            for j in range(i-1, -1, -1):
                prev_dt = datetime.fromisoformat(transfers[j]["metadata"]["blockTimestamp"].replace("Z", "+00:00"))
                if current_ts - prev_dt.timestamp() <= 3600:
                    recent_tx_count += 1
                else:
                    break
            tx_frequency = recent_tx_count
            
            processed_data.append({
                "amount":             amount,
                "token_type":         token_type,
                "hour":               hour,
                "day_of_week":        day_of_week,
                "gas_fee":            gas_fee,
                "is_new_address":     is_new_address,
                "time_since_last_tx": time_since_last_tx,
                "tx_frequency":       tx_frequency,
                "label":              0 # Assume normal for training
            })
            
        except Exception as e:
            print(f"Skipping tx {tx.get('hash', 'unknown')} due to error: {e}")
            continue
            
    return pd.DataFrame(processed_data)

def save_real_data(df, path="data/transactions_real.csv"):
    """
    Saves the processed real data to CSV.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)
    print(f"✓ Successfully saved {len(df)} transactions to {path}")

if __name__ == "__main__":
    if not ALCHEMY_API_KEY or ALCHEMY_API_KEY == "your_alchemy_api_key_here":
        print("Error: ALCHEMY_API_KEY not set in .env")
        exit(1)
        
    if not TARGET_WALLET or TARGET_WALLET == "0x0000000000000000000000000000000000000000":
        print("Error: TARGET_WALLET_ADDRESS not set in .env")
        exit(1)
        
    try:
        raw_transfers = fetch_eth_transfers(TARGET_WALLET)
        df_real = process_transfers(raw_transfers)
        save_real_data(df_real)
        
        print("\n── Feature Sample ──")
        print(df_real.head())
        
    except Exception as e:
        print(f"Failed to ingest data: {e}")
