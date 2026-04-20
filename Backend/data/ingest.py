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
    Fetch native ETH transfers for the wallet address using Alchemy.

    We query both outgoing (fromAddress) and incoming (toAddress) transfers
    because some monitored wallets are mostly receivers.
    """
    headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }

    def _query(direction_key, direction_value, req_id):
        payload = {
            "id": req_id,
            "jsonrpc": "2.0",
            "method": "alchemy_getAssetTransfers",
            "params": [
                {
                    direction_key: direction_value,
                    "category": ["external"],
                    "withMetadata": True,
                    "excludeZeroValue": False,
                    "maxCount": "0x3e8"
                }
            ]
        }
        response = requests.post(ALCHEMY_URL, json=payload, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Alchemy API error: {response.text}")
        result = response.json()
        if "result" not in result:
            raise Exception(f"Unexpected Alchemy response: {result}")
        return result["result"].get("transfers", [])

    print(f"Fetching history for: {wallet_address} (outgoing + incoming)...")
    outgoing = _query("fromAddress", wallet_address, 1)
    incoming = _query("toAddress", wallet_address, 2)

    # Deduplicate by stable transfer identifiers when available.
    seen = set()
    combined = []
    for tx in outgoing + incoming:
        key = (
            tx.get("hash"),
            tx.get("uniqueId"),
            tx.get("blockNum"),
            tx.get("from"),
            tx.get("to"),
            tx.get("value"),
        )
        if key in seen:
            continue
        seen.add(key)
        combined.append(tx)

    return combined

def process_transfers(transfers):
    """
    Transforms raw Alchemy transfers into the 8-feature schema.
    """
    transfers.sort(key=lambda x: int(x["blockNum"], 16))
    
    processed_data = []
    seen_destinations = set()
    last_tx_time = None
    
    print(f"Processing {len(transfers)} transactions...")

    for i, tx in enumerate(transfers):
        try:
            value = float(tx.get("value", 0) or 0)
            to_addr = (tx.get("to") or "").lower()
            ts_str = tx["metadata"]["blockTimestamp"]
            dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
            current_ts = dt.timestamp()
            
            amount = value
            token_type = 0
            hour = dt.hour
            day_of_week = dt.weekday()
            gas_fee = 0.0005
            
            is_new_address = 1 if to_addr not in seen_destinations else 0
            seen_destinations.add(to_addr)
            
            if last_tx_time is None:
                time_since_last_tx = 3600
            else:
                time_since_last_tx = int(current_ts - last_tx_time)
            last_tx_time = current_ts
            
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
                "label":              0
            })
            
        except Exception as e:
            continue
            
    return pd.DataFrame(processed_data)

def save_real_data(df, path="data/transactions_real.csv"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)
    print(f"Success: Saved {len(df)} transactions to {path}")

if __name__ == "__main__":
    if not ALCHEMY_API_KEY or ALCHEMY_API_KEY == "your_alchemy_api_key_here":
        exit(1)
    if not TARGET_WALLET:
        exit(1)
        
    try:
        raw_transfers = fetch_eth_transfers(TARGET_WALLET)
        print(f"Total raw transfers fetched: {len(raw_transfers)}")
        if len(raw_transfers) == 0:
            print("No transactions found.")
            exit(0)
        df_real = process_transfers(raw_transfers)
        save_real_data(df_real)
    except Exception as e:
        print(f"Failed to ingest data: {e}")
