from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from .database import engine, Base, get_db
from . import models

# Initialize Database on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Behavior-Based Manipulation Scoring API", version="1.0.0")

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Healthcheck endpoint to verify API and DB status."""
    try:
        # Simple query to ensure DB is connected
        db.execute("SELECT 1")
        return {"status": "ok", "db_connected": True}
    except Exception as e:
        return {"status": "unhealthy", "db_connected": False, "error": str(e)}

