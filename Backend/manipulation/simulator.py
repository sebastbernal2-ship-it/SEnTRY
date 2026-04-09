import time
import random
import requests
from datetime import datetime, timezone

API_URL = "http://localhost:8000"

PROFILES = {
    "benign": {
        "source_type": "user_wallet",
        "rate_range_seconds": (2.0, 5.0),    # Moderate frequency
        "size_range": (100.0, 500.0),        # Normal sizes
        "success_prob": 0.95,                # High success rate
        "destinations": ["0xVault1", "0xVaultC"]
    },
    "suspicious": {
        "source_type": "trading_bot",
        "rate_range_seconds": (0.5, 1.5),    # High frequency spike
        "size_range": (5000.0, 20000.0),     # Larger sizes
        "success_prob": 0.40,                # Lower success rate
        "destinations": ["0xPoolA", "0xPoolB"]
    },
    "manual_review": {
        "source_type": "unknown_script",
        "rate_range_seconds": (0.05, 0.2),   # Extreme burst
        "size_range": (10.0, 100000.0),      # Erratic sizes
        "success_prob": 0.05,                # Very low success (failing exploits)
        "destinations": ["0xHacker1", "0xHacker2", "0xHacker3", "0xMixerX"] # Erratic
    }
}

def simulate_events(duration_seconds=30):
    print(f"Starting simulation for {duration_seconds} seconds...")
    start_time = time.time()
    
    # Initialize tracking state
    sources = {
        "0x_Alice_Benign": {"profile": "benign", "next_time": start_time},
        "0x_Bob_Suspicious": {"profile": "suspicious", "next_time": start_time},
        "0x_Eve_Hacker": {"profile": "manual_review", "next_time": start_time}
    }
    
    events_sent = 0
    
    while time.time() - start_time < duration_seconds:
        now = time.time()
        for src_key, data in sources.items():
            if now >= data["next_time"]:
                prof_name = data["profile"]
                prof = PROFILES[prof_name]
                
                # Formulate dynamic event
                ev = {
                    "source_key": src_key,
                    "source_type": prof["source_type"],
                    "event_time": datetime.now(timezone.utc).isoformat(),
                    "event_type": "contract_interaction",
                    "proposal_size": random.uniform(prof["size_range"][0], prof["size_range"][1]),
                    "destination_address": random.choice(prof["destinations"]),
                    "success_flag": random.random() < prof["success_prob"],
                    "metadata": {
                        "simulation_profile": prof_name,
                        "generated_agent": "simulator_engine"
                    }
                }
                
                # Emit through standard ingestion pipeline
                try:
                    res = requests.post(f"{API_URL}/events", json=ev)
                    if res.status_code == 201:
                        events_sent += 1
                        print(f"[{prof_name.upper():<13}] {src_key} -> target: {ev['destination_address']}, size: {ev['proposal_size']:6.1f}, success: {ev['success_flag']}")
                except requests.exceptions.ConnectionError:
                    print("Connection error: API server not running.")
                    return
                
                # Schedule next event for this specific source
                delay = random.uniform(prof["rate_range_seconds"][0], prof["rate_range_seconds"][1])
                data["next_time"] = now + delay
                
        time.sleep(0.02) # Prevent CPU spinning
        
    print(f"\\nSimulation completed. Distributed {events_sent} synthetic events.")

if __name__ == "__main__":
    simulate_events(duration_seconds=15)
