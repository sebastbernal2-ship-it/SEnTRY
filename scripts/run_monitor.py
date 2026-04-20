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
import numpy as np
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
    manipulation_items: List[Dict[str, Any]],
    injection_items: List[Dict[str, Any]],
    aml_items: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Compute module summary statistics.
    
    Args:
        anomaly_items: Transaction anomaly results
        manipulation_items: Behavior manipulation results
        injection_items: Prompt injection results
        aml_items: Money laundering results
    
    Returns:
        Summary dict for frontend
    """
    def count_flagged(items, threshold=80):
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
                "key": "behavior_manipulation",
                "title": "Behavior Manipulation Scoring",
                "flagged_count": count_flagged(manipulation_items),
                "total_count": len(manipulation_items),
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
    manipulation_items: List[Dict[str, Any]],
    injection_items: List[Dict[str, Any]],
    aml_items: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Generate new alerts from scored items.
    
    Args:
        deduplicator: Alert deduplication manager
        anomaly_items: Transaction anomaly results
        manipulation_items: Behavior manipulation results
        injection_items: Prompt injection results
        aml_items: Money laundering results
    
    Returns:
        List of new alert dicts
    """
    new_alerts = []
    
    # Check transaction anomalies
    threshold = 80.0
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
    for item in manipulation_items:
        score = item.get("risk_score", 0)
        if should_send_notification(score, threshold):
            entity_id = item.get("id", "unknown")
            severity = item.get("severity", "high")

            if deduplicator.is_new_alert("behavior_manipulation", entity_id, severity):
                title = item.get("title", "Behavior Manipulation Risk Detected")
                reasons = item.get("reason_codes", [])
                description = f"Source {item.get('source_key', entity_id)} shows manipulative behavior (score: {score})"
                if reasons:
                    description = f"{description}. Factors: {', '.join(reasons)}"

                alert = format_alert_for_display(
                    alert_id=f"bhv-{entity_id}-{get_utc_now().replace(':', '').replace('-', '')}",
                    module="behavior_manipulation",
                    title=title,
                    description=description,
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


def compute_behavior_manipulation_scores(
    anomaly_items: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Compute a lightweight Module 2 behavior risk from transaction behavior patterns.

    This keeps Module 2 in the pipeline without requiring the standalone manipulation
    API server and database to be running in GitHub Actions.
    """
    behavior_items: List[Dict[str, Any]] = []

    for tx in anomaly_items:
        tx_freq = float(tx.get("tx_frequency", 0) or 0)
        amount = float(tx.get("amount", 0) or 0)
        is_new_address = float(tx.get("is_new_address", 0) or 0)
        time_since_last = float(tx.get("time_since_last_tx", 0) or 0)
        anomaly_score = float(tx.get("risk_score", 0) or 0)

        # Heuristic behavior score on a 0-100 scale.
        score = (
            min(65.0, anomaly_score * 0.6) +
            min(20.0, tx_freq * 1.5) +
            min(10.0, amount / 10.0) +
            (10.0 if is_new_address >= 1 else 0.0) +
            (10.0 if 0 < time_since_last < 60 else 0.0)
        )
        score = round(min(100.0, score), 2)

        if score >= 70:
            label = "High Risk"
            severity = "high"
        elif score >= 35:
            label = "Suspicious"
            severity = "medium"
        else:
            label = "Clean"
            severity = "low"

        reasons: List[str] = []
        if tx_freq >= 8:
            reasons.append("proposal frequency spike")
        if amount >= 25:
            reasons.append("unusually large proposal size")
        if is_new_address >= 1:
            reasons.append("new destination behavior")
        if 0 < time_since_last < 60:
            reasons.append("bursty repeated behavior")

        behavior_items.append({
            "id": f"src-{tx.get('id', 'unknown')}",
            "source_key": tx.get("id", "unknown"),
            "title": "Behavior Manipulation Risk Detected",
            "risk_score": score,
            "label": label,
            "severity": severity,
            "reason_codes": reasons,
            "linked_transaction_id": tx.get("id"),
        })

    return behavior_items


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
        use_demo_data: If True, generate demo data. If False, fetch real data from APIs.
    
    Returns:
        Summary of run results
    """
    ensure_dir(output_dir)
    ensure_dir(state_dir)
    
    logger.info("Starting S.E.N.T.R.Y. monitoring pipeline...")
    logger.info(f"Mode: {'DEMO DATA' if use_demo_data else 'REAL DATA'}")

    # In CI, keep anomaly model loading opt-in to avoid native crashes from
    # incompatible artifacts/libraries. Locally, default to enabled.
    default_anomaly_model = "false" if os.getenv("GITHUB_ACTIONS", "").lower() == "true" else "true"
    anomaly_use_model = os.getenv("ANOMALY_USE_MODEL", default_anomaly_model).lower() in ("true", "1", "yes")
    logger.info(f"Anomaly model enabled: {anomaly_use_model}")
    
    # Initialize modules
    anomaly_detector = TransactionAnomalyDetector(use_model=anomaly_use_model)
    injection_detector = PromptInjectionDetector()
    aml_detector = MoneyLaunderingDetector()
    
    # Initialize deduplicator
    alert_state_file = os.path.join(state_dir, "already_alerted.json")
    deduplicator = AlertDeduplicator(alert_state_file)
    
    # Generate or fetch data
    logger.info("Generating/fetching data...")
    
    if use_demo_data:
        logger.info("Using demo/synthetic data...")
        anomaly_transactions = anomaly_detector.generate_demo_transactions(8)
        injection_messages = injection_detector.generate_demo_messages(8)
        aml_addresses = aml_detector.generate_demo_addresses(8)
    else:
        logger.info("Fetching real data from APIs...")
        # Fetch real transaction data
        try:
            from Backend.data.ingest import fetch_eth_transfers, process_transfers
            
            # Get wallet address from environment
            target_wallet = os.getenv("TARGET_WALLET_ADDRESS")
            if not target_wallet:
                logger.error("TARGET_WALLET_ADDRESS environment variable not set. Cannot fetch real data.")
                logger.info("Falling back to demo data...")
                anomaly_transactions = anomaly_detector.generate_demo_transactions(8)
            else:
                try:
                    logger.info(f"Fetching transactions for {target_wallet}...")
                    transfers = fetch_eth_transfers(target_wallet)
                    processed = process_transfers(transfers)
                    processed_rows = processed.to_dict(orient="records")
                    anomaly_transactions = [
                        {
                            "id": f"tx_{i}",
                            "amount": row["amount"],
                            "token_type": row["token_type"],
                            "hour": row["hour"],
                            "day_of_week": row["day_of_week"],
                            "gas_fee": row["gas_fee"],
                            "is_new_address": row["is_new_address"],
                            "time_since_last_tx": row["time_since_last_tx"],
                            "tx_frequency": row["tx_frequency"],
                        }
                        for i, row in enumerate(processed_rows)
                    ]
                    logger.info(f"Fetched {len(anomaly_transactions)} real transactions")
                except Exception as e:
                    logger.error(f"Failed to fetch real data: {e}")
                    logger.info("Falling back to demo data...")
                    anomaly_transactions = anomaly_detector.generate_demo_transactions(8)
        except ImportError as e:
            logger.error(f"Could not import ingest module ({e}). Falling back to demo data...")
            anomaly_transactions = anomaly_detector.generate_demo_transactions(8)
        
        # For now, always use demo data for injection and AML (no APIs available yet)
        injection_messages = injection_detector.generate_demo_messages(8)
        aml_addresses = aml_detector.generate_demo_addresses(8)
    
    # Score all items
    logger.info("Scoring items...")
    anomaly_results = anomaly_detector.score_batch(anomaly_transactions)
    anomaly_scores = []
    for tx, score in zip(anomaly_transactions, anomaly_results):
        item = {**tx, **score}
        anomaly_scores.append(item)

    if anomaly_scores:
        anomaly_risks = np.array([float(item.get("risk_score", 0) or 0) for item in anomaly_scores], dtype=float)
        logger.info(
            "Anomaly score distribution: min=%.2f p50=%.2f p90=%.2f p95=%.2f max=%.2f",
            float(np.min(anomaly_risks)),
            float(np.percentile(anomaly_risks, 50)),
            float(np.percentile(anomaly_risks, 90)),
            float(np.percentile(anomaly_risks, 95)),
            float(np.max(anomaly_risks)),
        )
    
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

    # Compute behavior manipulation risk from transaction behavior.
    manipulation_scores = compute_behavior_manipulation_scores(anomaly_scores)
    
    # Compute summary
    summary = compute_summary(anomaly_scores, manipulation_scores, injection_scores, aml_scores)
    
    # Generate alerts
    logger.info("Generating alerts...")
    new_alerts = generate_alerts(deduplicator, anomaly_scores, manipulation_scores, injection_scores, aml_scores)
    
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
        os.path.join(output_dir, "behavior-manipulation.json"),
        {
            "module": "behavior_manipulation",
            "updated_at": get_utc_now(),
            "items": manipulation_scores,
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
        "manipulation_scored": len(manipulation_scores),
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
    
    # Check environment variable (takes precedence if set)
    use_real_data_env = os.getenv("USE_REAL_DATA", "").lower() in ("true", "1", "yes")
    use_real_data = args.use_real_data or use_real_data_env
    
    result = run_monitor(
        output_dir=args.output_dir,
        state_dir=args.state_dir,
        use_demo_data=not use_real_data,
    )
    
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "success" else 1


if __name__ == "__main__":
    sys.exit(main())
