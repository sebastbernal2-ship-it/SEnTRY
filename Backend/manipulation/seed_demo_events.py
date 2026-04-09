import requests
import json
from datetime import datetime, timezone

API_URL = "http://localhost:8000"

demo_events = [
    {
        "source_key": "0xabc123",
        "source_type": "wallet",
        "event_time": datetime.now(timezone.utc).isoformat(),
        "event_type": "proposal_received",
        "proposal_size": 2500.0,
        "destination_address": "0xdef456",
        "success_flag": False,
        "tx_hash": None,
        "metadata": {
            "chain": "ethereum",
            "network": "mainnet",
            "channel": "mempool"
        }
    },
    {
        "source_key": "0xabc123", # Duplicate source, should test upsert
        "source_type": "wallet",
        "event_time": datetime.now(timezone.utc).isoformat(),
        "event_type": "proposal_received",
        "proposal_size": 500.0,
        "destination_address": "0xdef456",
        "success_flag": True,
        "tx_hash": "0x111222333",
        "metadata": None
    },
    {
        "source_key": "0x999bot",
        "source_type": "bot",
        "event_time": datetime.now(timezone.utc).isoformat(),
        "event_type": "proposal_received",
        "proposal_size": 50000.0,
        "destination_address": "0xhacker",
        "success_flag": False,
        "tx_hash": None,
        "metadata": {"user_agent": "curl"}
    }
]

def seed_events():
    print("Seeding demo events...")
    for event in demo_events:
        response = requests.post(f"{API_URL}/events", json=event)
        if response.status_code == 201:
            print(f"Success: {response.json()}")
        else:
            print(f"Failed to post event: {response.status_code} - {response.text}")

if __name__ == "__main__":
    seed_events()
