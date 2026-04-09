from sqlalchemy.orm import Session
from datetime import datetime, timezone
from . import models

SEVERITY_MAP = {
    "suspicious": "warning",
    "manual_review": "critical"
}

def generate_alerts(db: Session):
    """
    Evaluates latest risk scores and generates deduplicated alerts
    for sources that cross into elevated risk tiers.
    """
    sources = db.query(models.Source).all()
    alerts_created = 0
    now = datetime.now(timezone.utc)
    
    for source in sources:
        # Get the latest score
        latest_score = db.query(models.SourceRiskScore).filter(
            models.SourceRiskScore.source_id == source.id
        ).order_by(models.SourceRiskScore.as_of_time.desc()).first()
        
        if not latest_score:
            continue
            
        if latest_score.risk_label in ["suspicious", "manual_review"]:
            severity = SEVERITY_MAP[latest_score.risk_label]
            
            # Simple Deduplication Rule:
            # Look at the most recent alert for this source
            last_alert = db.query(models.Alert).filter(
                models.Alert.source_id == source.id
            ).order_by(models.Alert.created_at.desc()).first()
            
            # If we already have an active alert of the same severity, don't spam
            if last_alert and last_alert.status == "open" and last_alert.severity == severity:
                continue
                
            # Otherwise, create a new alert. (e.g. going from warning -> critical)
            reasons = latest_score.reason_codes_json or []
            title = f"Source {source.source_key[:8]} flagged as {latest_score.risk_label.replace('_', ' ').title()}"
            message = f"Risk Score {latest_score.risk_score:.1f}. Factors: {', '.join(reasons)}"
            
            new_alert = models.Alert(
                source_id=source.id,
                created_at=now,
                severity=severity,
                title=title,
                message=message,
                reason_codes_json=reasons,
                status="open"  # other states could be 'resolved', 'ignored'
            )
            db.add(new_alert)
            alerts_created += 1
            
    db.commit()
    return alerts_created
