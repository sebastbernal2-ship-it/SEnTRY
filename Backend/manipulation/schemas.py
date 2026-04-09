from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class InteractionEventCreate(BaseModel):
    source_key: str
    source_type: str
    event_time: datetime
    event_type: str
    proposal_size: float
    destination_address: str
    success_flag: bool
    tx_hash: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "source_key": "0xabc123",
                "source_type": "wallet",
                "event_time": "2026-04-09T02:00:00Z",
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
            }
        }
