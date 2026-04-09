from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from .database import engine, Base, get_db
from . import models, schemas

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
