"""
Alert deduplication and notification logic.
"""
import hashlib
from typing import Dict, List, Any
from datetime import datetime, timedelta, timezone
from .io import read_json_file, write_json


class AlertDeduplicator:
    """
    Manages alert deduplication to avoid re-alerting on same anomalies.
    Uses stable signatures and TTL-based pruning.
    """

    def __init__(self, state_file: str):
        self.state_file = state_file
        self.alerted = read_json_file(state_file, {})

    def _alert_key(self, module: str, entity_id: str, severity: str) -> str:
        """Generate stable hash for alert deduplication."""
        composite = f"{module}:{entity_id}:{severity}"
        return hashlib.sha256(composite.encode()).hexdigest()[:16]

    def is_new_alert(self, module: str, entity_id: str, severity: str, ttl_hours: int = 24) -> bool:
        """
        Check if this is a new alert (not seen recently).
        
        Args:
            module: Module name (e.g., 'prompt_injection')
            entity_id: Unique entity identifier
            severity: Alert severity level
            ttl_hours: Hours before alert is forgotten (default 24)
        
        Returns:
            True if this is a new alert, False if already alerted recently
        """
        key = self._alert_key(module, entity_id, severity)
        
        if key not in self.alerted:
            # New alert, record it
            self.alerted[key] = datetime.now(timezone.utc).isoformat()
            self.save()
            return True
        
        # Check if TTL has expired
        last_alert_str = self.alerted[key]
        try:
            last_alert = datetime.fromisoformat(last_alert_str.replace('Z', '+00:00'))
            now = datetime.now(timezone.utc)
            elapsed = now - last_alert
            if elapsed > timedelta(hours=ttl_hours):
                # TTL expired, treat as new and update
                self.alerted[key] = now.isoformat()
                self.save()
                return True
        except ValueError:
            pass
        
        # Not new, already alerted
        return False

    def save(self) -> None:
        """Persist alert state to disk."""
        write_json(self.state_file, self.alerted)

    def prune_stale(self, ttl_hours: int = 24) -> None:
        """Remove old alert records (optional cleanup)."""
        now = datetime.now(timezone.utc)
        to_remove = []
        
        for key, timestamp_str in self.alerted.items():
            try:
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                if now - timestamp > timedelta(hours=ttl_hours):
                    to_remove.append(key)
            except ValueError:
                to_remove.append(key)
        
        for key in to_remove:
            del self.alerted[key]
        
        if to_remove:
            self.save()


def should_send_notification(score: float, severity_threshold: float = 80.0) -> bool:
    """
    Determine if a score warrants notification.
    
    Args:
        score: Risk score (0-100)
        severity_threshold: Score threshold for alerting (default 70)
    
    Returns:
        True if score exceeds threshold
    """
    return score >= severity_threshold


def format_alert_for_display(
    alert_id: str,
    module: str,
    title: str,
    description: str,
    severity: str,
    score: float,
    label: str,
    timestamp: str
) -> Dict[str, Any]:
    """Format alert data for frontend display."""
    return {
        "id": alert_id,
        "module": module,
        "title": title,
        "description": description,
        "severity": severity,
        "score": score,
        "label": label,
        "timestamp": timestamp
    }
