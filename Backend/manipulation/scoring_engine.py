from sqlalchemy.orm import Session
from datetime import datetime, timezone
import json
from manipulation import models
from manipulation.scoring_config import WEIGHTS, THRESHOLDS, REASON_THRESHOLDS, REASON_MESSAGES

def normalize_features(snapshot):
    """
    Normalizes feature values to a 0.0 - 1.0 range based on MVP bounds.
    """
    # Cap frequency spike at 5x = 1.0 score
    n_freq = min(1.0, snapshot.frequency_spike_score / 5.0) if snapshot.frequency_spike_score else 0.0
    
    # Failure rate (1 - success_rate)
    f_rate = 1.0 - (snapshot.success_rate if snapshot.success_rate is not None else 1.0)
    
    # Cap mean size at some arbitrary MVP threshold, e.g., 50k
    n_size = min(1.0, (snapshot.mean_size or 0) / 50000.0)
    
    # Size volatility: Coefficient of variation
    n_size_vol = 0.0
    if snapshot.mean_size and snapshot.size_std:
        n_size_vol = min(1.0, snapshot.size_std / snapshot.mean_size)
        
    # Destination shift: low concentration = high shift
    n_dest = 1.0 - snapshot.destination_concentration if snapshot.destination_concentration else 0.0
    # i think this line would be better: n_dest = (1.0 - snapshot.destination_concentration) if snapshot.destination_concentration is not None else 0.0

    # Burstiness: Interarrival CV > 1 indicates bursty clustering
    n_burst = 0.0
    if snapshot.interarrival_mean_seconds and snapshot.interarrival_std_seconds:
        n_burst = min(1.0, snapshot.interarrival_std_seconds / snapshot.interarrival_mean_seconds)

    return {
        "normalized_frequency_spike": n_freq,
        "failure_rate": f_rate,
        "normalized_mean_size": n_size,
        "normalized_size_volatility": n_size_vol,
        "normalized_destination_shift": n_dest,
        "normalized_burstiness": n_burst
    }

def score_all_sources(db: Session, window_name: str = "1h"):
    sources = db.query(models.Source).all()
    results = []
    now = datetime.now(timezone.utc)
    try:
        for source in sources:
            # Get latest snapshot for window
            snapshot = db.query(models.SourceFeatureSnapshot).filter(
                models.SourceFeatureSnapshot.source_id == source.id,
                models.SourceFeatureSnapshot.window_name == window_name
            ).order_by(models.SourceFeatureSnapshot.as_of_time.desc()).first()
            
            if not snapshot:
                continue
                
            norm = normalize_features(snapshot)
            
            # Base deterministic formula
            risk_score = 100.0 * (
                WEIGHTS["normalized_frequency_spike"] * norm["normalized_frequency_spike"] +
                WEIGHTS["failure_rate"] * norm["failure_rate"] +
                WEIGHTS["normalized_mean_size"] * norm["normalized_mean_size"] +
                WEIGHTS["normalized_size_volatility"] * norm["normalized_size_volatility"] +
                WEIGHTS["normalized_destination_shift"] * norm["normalized_destination_shift"] +
                WEIGHTS["normalized_burstiness"] * norm["normalized_burstiness"]
            )
            
            # Label mapping
            if risk_score < THRESHOLDS["suspicious"]:
                label = "benign"
            elif risk_score < THRESHOLDS["manual_review"]:
                label = "suspicious"
            else:
                label = "manual_review"
                
            # Reason code generation
            reasons = []
            if norm["normalized_frequency_spike"] > REASON_THRESHOLDS["frequency_spike"]:
                reasons.append(REASON_MESSAGES["frequency_spike"])
            if snapshot.success_rate is not None and snapshot.success_rate < REASON_THRESHOLDS["success_rate_min"]:
                reasons.append(REASON_MESSAGES["low_success"])
            if norm["normalized_mean_size"] > REASON_THRESHOLDS["mean_size"]:
                reasons.append(REASON_MESSAGES["large_size"])
            if norm["normalized_destination_shift"] > REASON_THRESHOLDS["destination_shift"]:
                reasons.append(REASON_MESSAGES["destination_change"])
            if norm["normalized_burstiness"] > REASON_THRESHOLDS["burstiness"]:
                reasons.append(REASON_MESSAGES["bursty"])
                
            score_record = models.SourceRiskScore(
                source_id=source.id,
                as_of_time=now,
                window_name=window_name,
                risk_score=risk_score,
                risk_label=label,
                reason_codes_json=reasons,
                model_version="v1.0-rules"
            )
            db.add(score_record)
            results.append(score_record)
            
        db.commit()
    except Exception:
        db.rollback()
        raise
    return len(results)
