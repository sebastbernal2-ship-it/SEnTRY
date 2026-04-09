import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone
from manipulation.main import app
from manipulation.database import Base, engine, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 1. Setup Ephemeral SQLite Database for Testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_manipulation.db"
test_engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

Base.metadata.create_all(bind=test_engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_and_teardown():
    # Teardown logic
    yield
    Base.metadata.drop_all(bind=test_engine)

# ====================
# Integration Tests
# ====================

def test_health_check():
    """Verify system standup."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_raw_event_ingestion():
    """Verify ingestion pipeline natively maps parameters and upserts sources."""
    event = {
        "source_key": "test_bot_001",
        "source_type": "bot",
        "event_time": datetime.now(timezone.utc).isoformat(),
        "event_type": "test_ping",
        "proposal_size": 1500.0,
        "destination_address": "0xtest_vault",
        "success_flag": False
    }
    response = client.post("/events", json=event)
    assert response.status_code == 201
    assert response.json()["status"] == "success"
    assert "event_id" in response.json()

def test_feature_computation():
    """Verify the rolling engineering metric aggregations."""
    response = client.post("/features/recompute")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["snapshots_created"] > 0

def test_deterministic_scoring_and_alerting():
    """Verify score mapping and operational telemetry."""
    response = client.post("/scoring/run", params={"window": "1h"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["scored_sources_count"] > 0
    # Alerts generated may be 0 or 1 depending on whether the test event crossed the threshold
    assert "alerts_generated" in data

def test_score_fetching():
    """Verify we can inspect a specific source object and check ML fallback behavior."""
    response = client.get("/scoring/test_bot_001")
    assert response.status_code == 200
    data = response.json()
    assert "risk_score" in data
    assert "label" in data
    assert "ml_label" in data # verifies the ML fallback architecture exists in the response
