import abc
import requests
from typing import List
from datetime import datetime, timezone

from manipulation.schemas import InteractionEventCreate

class BaseSourceAdapter(abc.ABC):
    """
    Base interface for ingesting events into the SEnTRY Manipulation Scorer.
    Any concrete adapter must implement `fetch_events` and map its native
    payload into the standardized `InteractionEventCreate` schema.
    """
    
    def __init__(self, target_api_url: str = "http://localhost:8000/events"):
        self.target_api_url = target_api_url

    @abc.abstractmethod
    def fetch_events(self) -> List[InteractionEventCreate]:
        """Fetches events from the specific source system and maps them to standard schema."""
        pass
        
    def push_events(self):
        """Standardized pipeline to push fetched events into the ingestion API."""
        events = self.fetch_events()
        pushed_count = 0
        for event in events:
            try:
                # model_dump(mode='json') automatically handles datetime serialization
                res = requests.post(self.target_api_url, json=event.model_dump(mode='json'))
                if res.status_code == 201:
                    pushed_count += 1
            except Exception as e:
                print(f"Failed to push event: {e}")
        return pushed_count


# --- 1. App-Native Logs Adapter (Concrete Implementation) ---
class AppLogAdapter(BaseSourceAdapter):
    """
    Reads from local application logs inside the main app.
    Here we map standard Python dictionary logs into the anomaly engine.
    """
    def __init__(self, log_stream: List[dict], target_api_url: str = "http://localhost:8000/events"):
        super().__init__(target_api_url)
        self.log_stream = log_stream
        
    def fetch_events(self) -> List[InteractionEventCreate]:
        mapped = []
        for log in self.log_stream:
            try:
                # App logs natively have similar fields but might be named differently
                event = InteractionEventCreate(
                    source_key=log.get("user_session_id", "unknown_user"),
                    source_type="app_session",
                    event_time=log.get("timestamp", datetime.now(timezone.utc)),
                    event_type=log.get("action", "interface_click"),
                    proposal_size=float(log.get("trade_size_usd", 0.0)),
                    destination_address=log.get("to_address", "internal_routing"),
                    success_flag=log.get("status") == "success",
                    metadata={"provider": "app_logs", "ip": log.get("ip_address")}
                )
                mapped.append(event)
            except Exception as e:
                print(f"Skipping malformed app log: {e}")
        return mapped


# --- 2. Blockchain Transaction Feed Adapter (Template/Mocked) ---
class BlockchainAdapter(BaseSourceAdapter):
    """
    Template for connecting to a real provider like Alchemy or Infura.
    If creds are provided, it connects to real WebSockets/RPC.
    Otherwise, it yields mocked blocks.
    """
    def __init__(self, rpc_url: str = None, target_api_url: str = "http://localhost:8000/events"):
        super().__init__(target_api_url)
        self.rpc_url = rpc_url
        
    def fetch_events(self) -> List[InteractionEventCreate]:
        if not self.rpc_url:
            print("No RPC URL provided. Yielding mock block data...")
            return self._mock_block_fetch()
            
        # REAL IMPLEMENTATION TEMPLATE:
        # 1. raw_txs = requests.post(self.rpc_url, json={"method": "eth_getBlockByNumber", ...}).json()
        # 2. Iterate raw_txs, decode input data if needed.
        # 3. Construct InteractionEventCreate models.
        # return mapped_list
        return []

    def _mock_block_fetch(self) -> List[InteractionEventCreate]:
        return [
            InteractionEventCreate(
                source_key="0x_MOCKED_SENDER",
                source_type="onchain_wallet",
                event_time=datetime.now(timezone.utc),
                event_type="contract_call",
                proposal_size=15.5, # ETH
                destination_address="0x_TARGET_CONTRACT",
                success_flag=True,
                tx_hash="0xabc123...def",
                metadata={"network": "ethereum", "chain_id": 1, "is_mocked": True}
            )
        ]


# --- 3. Mempool Feed Adapter (Template) ---
class MempoolAdapter(BaseSourceAdapter):
    """
    Template for connecting to a mempool stream (e.g., Blocknative WebSocket).
    Crucial for detecting manipulation attempts before they are finalized.
    """
    def __init__(self, ws_url: str = None, target_api_url: str = "http://localhost:8000/events"):
        super().__init__(target_api_url)
        self.ws_url = ws_url

    def fetch_events(self) -> List[InteractionEventCreate]:
        if not self.ws_url:
            print("No WebSocket URL provided for mempool. Yielding empty.")
            return []
            
        # 1. Connect to WSS
        # 2. Subscribe to pending transactions
        # 3. Stream payloads and map to InteractionEventCreate
        return []
