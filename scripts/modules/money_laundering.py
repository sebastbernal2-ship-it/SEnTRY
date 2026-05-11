"""
Anti-Money Laundering (AML) Detection Module
Scores addresses for on-chain topology risks and mixing patterns.
"""
import random
import hashlib
from typing import Dict, Any, List

from ..utils.scoring import score_to_label, score_to_severity
from ..utils.io import get_utc_now


class MoneyLaunderingDetector:
    """Detects AML risks in counterparty addresses."""

    def __init__(self):
        """Initialize detector."""
        pass

    def _is_known_mixer(self, address: str) -> bool:
        """
        Check if address matches known mixing service patterns.
        In production, this would query a blockchain analytics API.
        
        Args:
            address: Ethereum address
        
        Returns:
            True if likely a known mixer
        """
        # Oversimplified for demo: check substring patterns
        mixers = ["tornado", "mixer", "privacy", "0x400", "0x500"]
        return any(mixer in address.lower() for mixer in mixers)

    def _score_fan_out(self, fan_out: str) -> float:
        """Score based on fan-out (number of distinct recipients)."""
        fan_out_scores = {
            "Low": 5,
            "Medium": 20,
            "High": 35,
            "Very High": 45,
        }
        return float(fan_out_scores.get(fan_out, 10))

    def _score_burst_activity(self, burst_activity: bool) -> float:
        """Score based on burst activity patterns (sudden volume spikes)."""
        return 25.0 if burst_activity else 0.0

    def _score_mixer_contact(self, mixer_contact: bool) -> float:
        """Score based on direct contact with mixing services.

        Mixer contact is the strongest single AML signal, so it dominates the
        composite score.
        """
        return 45.0 if mixer_contact else 0.0

    def score_address(self, address_data: Dict[str, Any]) -> Dict[str, Any]:
        """Score an address for AML risk and return a structured breakdown."""
        address = address_data.get("address", "")
        fan_out = address_data.get("fan_out", "Low")
        burst_activity = address_data.get("burst_activity", False)
        mixer_contact = address_data.get("mixer_contact", False)

        # Additive composite — every signal contributes independently, with
        # mixer contact alone enough to push an address into "Suspicious."
        fan_out_score = self._score_fan_out(fan_out)
        burst_score = self._score_burst_activity(burst_activity)
        mixer_score = self._score_mixer_contact(mixer_contact)

        risk_score = fan_out_score + burst_score + mixer_score

        # Compounding penalty: multiple signals together signal active laundering.
        active_signals = sum([
            1 if mixer_contact else 0,
            1 if burst_activity else 0,
            1 if fan_out in ("High", "Very High") else 0,
        ])
        if active_signals >= 2:
            risk_score += 10
        if active_signals >= 3:
            risk_score += 10

        if self._is_known_mixer(address):
            risk_score += 25

        risk_score = float(min(max(risk_score, 0.0), 100.0))

        reason_codes: List[str] = []
        if mixer_contact:
            reason_codes.append("direct mixer contact")
        if burst_activity:
            reason_codes.append("burst transaction activity")
        if fan_out in ("High", "Very High"):
            reason_codes.append(f"{fan_out.lower()} counterparty fan-out")
        if self._is_known_mixer(address):
            reason_codes.append("address matches known mixer pattern")

        label = score_to_label(risk_score)
        severity = score_to_severity(risk_score)

        return {
            "risk_score": round(risk_score, 2),
            "label": label,
            "severity": severity,
            "address": address,
            "fan_out": fan_out,
            "burst_activity": burst_activity,
            "mixer_contact": mixer_contact,
            "reason_codes": reason_codes,
        }

    def score_batch(self, addresses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Score multiple addresses."""
        return [self.score_address(addr) for addr in addresses]

    def generate_demo_addresses(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        Generate demo address data for testing.
        
        Args:
            count: Number of demo addresses
        
        Returns:
            List of demo address dicts
        """
        samples = [
            {
                "address": "0xaB3f...221C",
                "fan_out": "Low",
                "burst_activity": False,
                "mixer_contact": False,
            },
            {
                "address": "0x9f2A...88BD",
                "fan_out": "High",
                "burst_activity": True,
                "mixer_contact": False,
            },
            {
                "address": "0xDEAD...BEEF",
                "fan_out": "Very High",
                "burst_activity": True,
                "mixer_contact": True,
            },
            {
                "address": "0x5544...33CC",
                "fan_out": "Low",
                "burst_activity": False,
                "mixer_contact": False,
            },
            {
                "address": "0xABCD...1234",
                "fan_out": "Medium",
                "burst_activity": False,
                "mixer_contact": False,
            },
            {
                "address": "0x9999...FFFF",
                "fan_out": "High",
                "burst_activity": True,
                "mixer_contact": False,
            },
            {
                "address": "0xCCCC...DDDD",
                "fan_out": "Low",
                "burst_activity": False,
                "mixer_contact": False,
            },
            {
                "address": "0xEEEE...0000",
                "fan_out": "Very High",
                "burst_activity": True,
                "mixer_contact": True,
            },
            {
                "address": "0x1111...2222",
                "fan_out": "Medium",
                "burst_activity": False,
                "mixer_contact": False,
            },
            {
                "address": "0x3333...4444",
                "fan_out": "High",
                "burst_activity": True,
                "mixer_contact": False,
            },
        ]
        
        addresses = []
        for i in range(min(count, len(samples))):
            sample = samples[i % len(samples)]
            sample["id"] = f"addr-{i:04d}"
            addresses.append(sample)
        return addresses
