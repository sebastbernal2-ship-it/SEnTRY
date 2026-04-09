from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from manipulation.database import engine, Base, get_db
from manipulation import models, schemas

# Initialize Database on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Behavior-Based Manipulation Scoring API", version="1.0.0")

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Healthcheck endpoint to verify API and DB status."""
    try:
        # Simple query to ensure DB is connected
        db.execute(text("SELECT 1"))
        return {"status": "ok", "db_connected": True}
    except Exception as e:
        return {"status": "unhealthy", "db_connected": False, "error": str(e)}

@app.post("/events", status_code=201)
def create_event(event_in: schemas.InteractionEventCreate, db: Session = Depends(get_db)):
    """Ingest an interaction event, upserting the source if it doesn't exist."""
    # 1. Upsert Source
    source = db.query(models.Source).filter(
        models.Source.source_key == event_in.source_key,
        models.Source.source_type == event_in.source_type
    ).first()

    if not source:
        source = models.Source(
            source_key=event_in.source_key,
            source_type=event_in.source_type,
            display_name=f"Auto-{event_in.source_key[:6]}"
        )
        db.add(source)
        db.flush() # flush to get source.id

    # 2. Insert Raw Event
    db_event = models.InteractionEvent(
        source_id=source.id,
        event_time=event_in.event_time,
        event_type=event_in.event_type,
        proposal_size=event_in.proposal_size,
        destination_address=event_in.destination_address,
        success_flag=event_in.success_flag,
        tx_hash=event_in.tx_hash,
        metadata_json=event_in.metadata
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    
    return {"status": "success", "event_id": db_event.id}

@app.get("/events")
def list_events(limit: int = 50, db: Session = Depends(get_db)):
    """Simple debugging endpoint to list recent events."""
    events = db.query(models.InteractionEvent).order_by(models.InteractionEvent.event_time.desc()).limit(limit).all()
    # Simple dictionary representation for debug endpoint
    return [{
        "id": e.id,
        "source_id": e.source_id,
        "event_time": e.event_time,
        "event_type": e.event_type,
        "proposal_size": e.proposal_size,
        "success_flag": e.success_flag
    } for e in events]

from manipulation.feature_engine import recompute_features

@app.post("/features/recompute")
def post_recompute_features(db: Session = Depends(get_db)):
    """Triggers the rolling window aggregation to compute feature snapshots."""
    snapshots_created = recompute_features(db)
    return {"status": "success", "snapshots_created": snapshots_created}

@app.get("/features/{source_key}")
def get_latest_features(source_key: str, db: Session = Depends(get_db)):
    """Fetch the latest feature snapshots for a given source key."""
    source = db.query(models.Source).filter(models.Source.source_key == source_key).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
        
    snapshots = db.query(models.SourceFeatureSnapshot).filter(
        models.SourceFeatureSnapshot.source_id == source.id
    ).order_by(models.SourceFeatureSnapshot.as_of_time.desc()).limit(4).all()
    
    return {
        "source_key": source_key,
        "snapshots": [
            {
                "window": s.window_name,
                "as_of_time": s.as_of_time,
                "interaction_count": s.interaction_count,
                "success_rate": s.success_rate,
                "frequency_spike_score": s.frequency_spike_score,
                "mean_size": s.mean_size
            } for s in snapshots
        ]
    }

from manipulation.scoring_engine import score_all_sources
from manipulation.alert_engine import generate_alerts

@app.post("/scoring/run")
def post_run_scoring(window: str = "1h", db: Session = Depends(get_db)):
    """Runs the deterministic scoring engine for all sources based on recent snapshots, then generates alerts."""
    count = score_all_sources(db, window_name=window)
    alerts_created = generate_alerts(db)
    return {
        "status": "success", 
        "scored_sources_count": count,
        "alerts_generated": alerts_created
    }

@app.get("/alerts")
def get_alerts(limit: int = 50, status: str = "open", db: Session = Depends(get_db)):
    """Fetch active alerts, optionally filtered by status."""
    query = db.query(models.Alert)
    if status != "all":
         query = query.filter(models.Alert.status == status)
         
    alerts = query.order_by(models.Alert.created_at.desc()).limit(limit).all()
    
    return [{
        "id": a.id,
        "source_id": a.source_id,
        "severity": a.severity,
        "title": a.title,
        "message": a.message,
        "reasons": a.reason_codes_json,
        "created_at": a.created_at,
        "status": a.status
    } for a in alerts]

from manipulation.ml_classifier import predict as predict_ml

@app.get("/scoring/{source_key}")
def get_latest_score(source_key: str, db: Session = Depends(get_db)):
    """Fetch the latest risk score and reason codes for a given source key."""
    source = db.query(models.Source).filter(models.Source.source_key == source_key).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
        
    score = db.query(models.SourceRiskScore).filter(
        models.SourceRiskScore.source_id == source.id
    ).order_by(models.SourceRiskScore.as_of_time.desc()).first()
    
    if not score:
        return {"status": "no_score_available"}

    # Fetch snapshot to run live ML inference alongside retrieving deterministic score
    snapshot = db.query(models.SourceFeatureSnapshot).filter(
        models.SourceFeatureSnapshot.source_id == source.id,
        models.SourceFeatureSnapshot.window_name == score.window_name
    ).order_by(models.SourceFeatureSnapshot.as_of_time.desc()).first()
    
    ml_label = predict_ml(snapshot) if snapshot else "N/A"
        
    return {
        "source_key": source_key,
        "risk_score": score.risk_score,
        "label": score.risk_label,            # Rule-engine classification
        "ml_label": ml_label,                 # ML-engine classification
        "reasons": score.reason_codes_json,
        "as_of_time": score.as_of_time,
        "window": score.window_name
    }
