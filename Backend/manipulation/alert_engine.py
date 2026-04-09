from sqlalchemy.orm import Session
from datetime import datetime, timezone
from manipulation import models

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
            
        # Current risk tier
        current_label = latest_score.risk_label
        
        # Find all active (open) alerts for this source
        open_alerts = db.query(models.Alert).filter(
            models.Alert.source_id == source.id,
            models.Alert.status == "open"
        ).all()
        
        if current_label in ["suspicious", "manual_review"]:
            severity = SEVERITY_MAP[current_label]
            
            # Check if we already have an alert for this EXACT severity level
            if any(a.severity == severity for a in open_alerts):
                continue
                
            # If we are here, either the severity changed (escalation/de-escalation) 
            # or there is no open alert.
            # 1. Resolve all previous open alerts to avoid double-counting
            for a in open_alerts:
                a.status = "resolved"
                
            # 2. Create the new updated alert
            reasons = latest_score.reason_codes_json or []
            title = f"Source {source.source_key[:8]} flagged as {current_label.replace('_', ' ').title()}"
            message = f"Risk Score {latest_score.risk_score:.1f}. Factors: {', '.join(reasons)}"
            
            new_alert = models.Alert(
                source_id=source.id,
                created_at=now,
                severity=severity,
                title=title,
                message=message,
                reason_codes_json=reasons,
                status="open"
            )
            db.add(new_alert)
            alerts_created += 1
        else:
            # Source returned to benign. Resolve any remaining open alerts.
            for a in open_alerts:
                a.status = "resolved"
            
    db.commit()
    return alerts_created
