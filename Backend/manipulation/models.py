from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from manipulation.database import Base

class Source(Base):
    __tablename__ = "sources"
    id = Column(Integer, primary_key=True, index=True)
    source_key = Column(String, unique=True, index=True)
    source_type = Column(String)
    display_name = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class InteractionEvent(Base):
    __tablename__ = "interaction_events"
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"))
    event_time = Column(DateTime(timezone=True), index=True)
    event_type = Column(String)
    proposal_size = Column(Float)
    destination_address = Column(String)
    success_flag = Column(Boolean)
    tx_hash = Column(String, nullable=True)
    metadata_json = Column(JSON, nullable=True)

class SourceFeatureSnapshot(Base):
    __tablename__ = "source_feature_snapshots"
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"))
    as_of_time = Column(DateTime(timezone=True))
    window_name = Column(String)
    interaction_count = Column(Integer)
    success_count = Column(Integer)
    failure_count = Column(Integer)
    success_rate = Column(Float)
    mean_size = Column(Float)
    median_size = Column(Float)
    size_std = Column(Float)
    unique_destinations = Column(Integer)
    destination_concentration = Column(Float)
    interarrival_mean_seconds = Column(Float)
    interarrival_std_seconds = Column(Float)
    frequency_spike_score = Column(Float)
    size_spike_score = Column(Float)
    trend_slope = Column(Float)

class SourceRiskScore(Base):
    __tablename__ = "source_risk_scores"
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"))
    as_of_time = Column(DateTime(timezone=True))
    window_name = Column(String)
    risk_score = Column(Float)
    risk_label = Column(String)
    reason_codes_json = Column(JSON)
    model_version = Column(String)

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    severity = Column(String)
    title = Column(String)
    message = Column(String)
    reason_codes_json = Column(JSON)
    status = Column(String)
