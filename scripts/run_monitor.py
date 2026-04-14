#!/usr/bin/env python3
"""
S.E.N.T.R.Y. Monitoring Pipeline
Runs analysis modules and generates JSON data for frontend consumption.
Designed to be invoked by GitHub Actions on a schedule.

Usage:
    python scripts/run_monitor.py [--output-dir ./Frontend/public/data] [--state-dir ./state]
"""
import sys
import os
import json
import argparse
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List

# Add project root to path (safe fallback)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.utils.io import read_json_file, write_json, get_utc_now, ensure_dir
from scripts.utils.alerts import AlertDeduplicator, should_send_notification, format_alert_for_display
from scripts.utils.notifications import send_notifications
from scripts.modules.transaction_anomaly import TransactionAnomalyDetector
from scripts.modules.prompt_injection import PromptInjectionDetector
from scripts.modules.money_laundering import MoneyLaunderingDetector


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


def compute_summary(
    anomaly_items: List[Dict[str, Any]],
    injection_items: List[Dict[str, Any]],
    aml_items: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Compute module summary statistics.
    
    Args:
        anomaly_items: Transaction anomaly results
        injection_items: Prompt injection results
        aml_items: Money laundering results
    
    Returns:
        Summary dict for frontend
    """
    def count_flagged(items, threshold=70):
        return sum(1 for item in items if item.get("risk_score", 0) >= threshold)
    
    return {
        "updated_at": get_utc_now(),
        "scan_status": "ok",
        "modules": [
            {
                "key": "transaction_anomaly",
                "title": "Transaction Anomaly Detection",
                "flagged_count": count_flagged(anomaly_items),
                "total_count": len(anomaly_items),
            },
            {
                "key": "prompt_injection",
                "title": "Prompt Injection Detection",
                "flagged_count": count_flagged(injection_items),
                "total_count": len(injection_items),
            },
            {
                "key": "money_laundering",
                "title": "Anti-Money Laundering Detection",
                "flagged_count": count_flagged(aml_items),
                "total_count": len(aml_items),
            },
        ]
    }


def generate_alerts(
    deduplicator: AlertDeduplicator,
    anomaly_items: List[Dict[str, Any]],
    injection_items: List[Dict[str, Any]],
    aml_items: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Generate new alerts from scored items.
    
    Args:
        deduplicator: Alert deduplication manager
        anomaly_items: Transaction anomaly results
        injection_items: Prompt injection results
        aml_items: Money laundering results
    
    Returns:
        List of new alert dicts
    """
    new_alerts = []
    
    # Check transaction anomalies
    threshold = 70.0
    for item in anomaly_items:
        score = item.get("risk_score", 0)
        if should_send_notification(score, threshold):
            entity_id = item.get("id", "unknown")
            severity = item.get("severity", "high")
            
            if deduplicator.is_new_alert("transaction_anomaly", entity_id, severity):
                alert = format_alert_for_display(
                    alert_id=f"txm-{entity_id}-{get_utc_now().replace(':', '').replace('-', '')}",
                    module="transaction_anomaly",
                    title="Anomalous Transaction Behavior",
                    description=f"Transaction {entity_id} flagged as anomalous (score: {score})",
                    severity=severity,
                    score=score,
                    label=item.get("label", "Unknown"),
                    timestamp=get_utc_now(),
                )
                new_alerts.append(alert)
    
    # Check prompt injection/manipulation
    for item in injection_items:
        score = item.get("risk_score", 0)
        if should_send_notification(score, threshold):
            entity_id = item.get("id", "unknown")
            severity = item.get("severity", "high")
            
            if deduplicator.is_new_alert("prompt_injection", entity_id, severity):
                alert = format_alert_for_display(
                    alert_id=f"inj-{entity_id}-{get_utc_now().replace(':', '').replace('-', '')}",
                    module="prompt_injection",
                    title="Manipulative Communication Detected",
                    description=f"Message contains manipulative patterns (score: {score})",
                    severity=severity,
                    score=score,
                    label=item.get("label", "Unknown"),
                    timestamp=get_utc_now(),
                )
                new_alerts.append(alert)
    
    # Check AML risks
    for item in aml_items:
        score = item.get("risk_score", 0)
        if should_send_notification(score, threshold):
            entity_id = item.get("id", "unknown")
            severity = item.get("severity", "high")
            
            if deduplicator.is_new_alert("money_laundering", entity_id, severity):
                address = item.get("address", "unknown")
                alert = format_alert_for_display(
                    alert_id=f"aml-{entity_id}-{get_utc_now().replace(':', '').replace('-', '')}",
                    module="money_laundering",
                    title="High-Risk Address Detected",
                    description=f"Address {address} shows risky AML patterns (score: {score})",
                    severity=severity,
                    score=score,
                    label=item.get("label", "Unknown"),
                    timestamp=get_utc_now(),
                )
                new_alerts.append(alert)
    
    return new_alerts


def run_monitor(
    output_dir: str,
    state_dir: str,
    use_demo_data: bool = True,
) -> Dict[str, Any]:
    """
    Main monitoring pipeline.
    
    Args:
        output_dir: Directory to write JSON files (e.g., Frontend/public/data)
        state_dir: Directory for state files (e.g., state/)
        use_demo_data: If True, generate demo data. If False, would fetch real data.
    
    Returns:
        Summary of run results
    """
    ensure_dir(output_dir)
    ensure_dir(state_dir)
    
    logger.info("Starting S.E.N.T.R.Y. monitoring pipeline...")
    
    # Initialize modules
    anomaly_detector = TransactionAnomalyDetector(use_model=True)
    injection_detector = PromptInjectionDetector()
    aml_detector = MoneyLaunderingDetector()
    
    # Initialize deduplicator
    alert_state_file = os.path.join(state_dir, "already_alerted.json")
    deduplicator = AlertDeduplicator(alert_state_file)
    
    # Generate or fetch data (demo mode for now)
    logger.info("Generating/fetching data...")
    
    if use_demo_data:
        anomaly_transactions = anomaly_detector.generate_demo_transactions(8)
        injection_messages = injection_detector.generate_demo_messages(8)
        aml_addresses = aml_detector.generate_demo_addresses(8)
    else:
        # TODO: In production, fetch real data from APIs/databases
        anomaly_transactions = []
        injection_messages = []
        aml_addresses = []
    
    # Score all items
    logger.info("Scoring items...")
    anomaly_scores = []
    for tx in anomaly_transactions:
        score = anomaly_detector.score_transaction(tx)
        item = {**tx, **score}
        anomaly_scores.append(item)
    
    injection_scores = []
    for msg in injection_messages:
        score = injection_detector.score_message(msg)
        item = {**msg, **score}
        injection_scores.append(item)
    
    aml_scores = []
    for addr in aml_addresses:
        score = aml_detector.score_address(addr)
        item = {**addr, **score}
        aml_scores.append(item)
    
    # Compute summary
    summary = compute_summary(anomaly_scores, injection_scores, aml_scores)
    
    # Generate alerts
    logger.info("Generating alerts...")
    new_alerts = generate_alerts(deduplicator, anomaly_scores, injection_scores, aml_scores)
    
    # Prepare output files
    logger.info(f"Writing output to {output_dir}...")
    
    # 1. Summary
    write_json(
        os.path.join(output_dir, "summary.json"),
        summary
    )
    
    # 2. Latest alerts
    alerts_data = {
        "updated_at": get_utc_now(),
        "new_alert_count": len(new_alerts),
        "alerts": new_alerts,
    }
    write_json(
        os.path.join(output_dir, "latest-alerts.json"),
        alerts_data
    )
    
    # 3. Module-specific data
    write_json(
        os.path.join(output_dir, "transaction-anomaly.json"),
        {
            "module": "transaction_anomaly",
            "updated_at": get_utc_now(),
            "items": anomaly_scores,
        }
    )
    
    write_json(
        os.path.join(output_dir, "prompt-injection.json"),
        {
            "module": "prompt_injection",
            "updated_at": get_utc_now(),
            "items": injection_scores,
        }
    )
    
    write_json(
        os.path.join(output_dir, "money-laundering.json"),
        {
            "module": "money_laundering",
            "updated_at": get_utc_now(),
            "items": aml_scores,
        }
    )
    
    # Save updated alert state
    deduplicator.save()
    
    # Send notifications (email, webhooks, etc.)
    logger.info("Sending notifications...")
    notification_result = send_notifications(new_alerts)
    logger.info(f"Notifications sent - email: {notification_result['email']}, webhooks: {notification_result['webhook']}")
    
    logger.info(f"Monitoring complete. Generated {len(new_alerts)} new alerts.")
    
    return {
        "status": "success",
        "new_alerts": len(new_alerts),
        "anomalies_scored": len(anomaly_scores),
        "messages_scored": len(injection_scores),
        "addresses_scored": len(aml_scores),
        "output_dir": output_dir,
    }


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="S.E.N.T.R.Y. Monitoring Pipeline"
    )
    parser.add_argument(
        "--output-dir",
        default="./Frontend/public/data",
        help="Directory to write JSON files (default: ./Frontend/public/data)"
    )
    parser.add_argument(
        "--state-dir",
        default="./state",
        help="Directory for state files (default: ./state)"
    )
    parser.add_argument(
        "--use-real-data",
        action="store_true",
        help="Use real data instead of demo (requires API keys)"
    )
    
    args = parser.parse_args()
    
    result = run_monitor(
        output_dir=args.output_dir,
        state_dir=args.state_dir,
        use_demo_data=not args.use_real_data,
    )
    
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "success" else 1


if __name__ == "__main__":
    sys.exit(main())
