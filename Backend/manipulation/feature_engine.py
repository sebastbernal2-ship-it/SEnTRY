from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from collections import Counter
import statistics
from . import models

WINDOWS = {
    "1m": timedelta(minutes=1),
    "5m": timedelta(minutes=5),
    "1h": timedelta(hours=1),
    "24h": timedelta(hours=24)
}

def recompute_features(db: Session):
    """
    Computes rolling metrics for each source across multiple time windows
    and persists them as feature snapshots.
    """
    now = datetime.now(timezone.utc)
    sources = db.query(models.Source).all()
    snapshots_created = 0

    for source in sources:
        for w_name, w_delta in WINDOWS.items():
            start_time = now - w_delta
            
            # 1. Fetch current window events
            curr_events = db.query(models.InteractionEvent).filter(
                models.InteractionEvent.source_id == source.id,
                models.InteractionEvent.event_time >= start_time,
                models.InteractionEvent.event_time <= now
            ).order_by(models.InteractionEvent.event_time.asc()).all()

            # 2. Fetch previous window events (for baseline/spike computation)
            prev_start = start_time - w_delta
            prev_events = db.query(models.InteractionEvent).filter(
                models.InteractionEvent.source_id == source.id,
                models.InteractionEvent.event_time >= prev_start,
                models.InteractionEvent.event_time < start_time
            ).all()

            interaction_count = len(curr_events)
            if interaction_count == 0:
                continue # Skip windows with no activity

            # Basic Counts & Rates
            success_count = sum(1 for e in curr_events if e.success_flag)
            failure_count = interaction_count - success_count
            success_rate = success_count / interaction_count

            # Size metrics
            sizes = [e.proposal_size for e in curr_events if e.proposal_size is not None]
            mean_size = statistics.mean(sizes) if sizes else 0.0
            median_size = statistics.median(sizes) if sizes else 0.0
            size_std = statistics.stdev(sizes) if len(sizes) > 1 else 0.0

            # Destination metrics
            dests = [e.destination_address for e in curr_events if e.destination_address]
            unique_destinations = len(set(dests))
            
            dest_counts = Counter(dests)
            max_dest_count = max(dest_counts.values()) if dest_counts else 0
            destination_concentration = max_dest_count / interaction_count if interaction_count > 0 else 0.0

            # Interarrival Times
            interarrival_mean_seconds = 0.0
            interarrival_std_seconds = 0.0
            if len(curr_events) > 1:
                # Ensure we use UTC for math
                times = [e.event_time if e.event_time.tzinfo else e.event_time.replace(tzinfo=timezone.utc) for e in curr_events]
                delays = [(times[i] - times[i-1]).total_seconds() for i in range(1, len(times))]
                interarrival_mean_seconds = statistics.mean(delays)
                interarrival_std_seconds = statistics.stdev(delays) if len(delays) > 1 else 0.0

            # Spike Scores
            prev_count = len(prev_events)
            frequency_spike_score = float(interaction_count) / prev_count if prev_count > 0 else float(interaction_count)

            prev_sizes = [e.proposal_size for e in prev_events if e.proposal_size is not None]
            prev_mean_size = statistics.mean(prev_sizes) if prev_sizes else 0.0
            # If there's a baseline, take ratio. If no baseline, magnitude is the spike score
            size_spike_score = float(mean_size) / prev_mean_size if prev_mean_size > 0 else (mean_size if prev_count == 0 else 0.0)

            # Trend Slope (Linear regression of size over time)
            trend_slope = 0.0
            if len(sizes) > 1:
                y = sizes
                times_arr = [e.event_time if e.event_time.tzinfo else e.event_time.replace(tzinfo=timezone.utc) for e in curr_events]
                t0 = times_arr[0]
                xs = [(t - t0).total_seconds() for t in times_arr]
                
                x_bar = statistics.mean(xs)
                y_bar = statistics.mean(y)
                
                num = sum((xi - x_bar) * (yi - y_bar) for xi, yi in zip(xs, y))
                den = sum((xi - x_bar)**2 for xi in xs)
                if den != 0:
                    trend_slope = num / den

            # 3. Create Feature Snapshot
            snapshot = models.SourceFeatureSnapshot(
                source_id=source.id,
                as_of_time=now,
                window_name=w_name,
                interaction_count=interaction_count,
                success_count=success_count,
                failure_count=failure_count,
                success_rate=success_rate,
                mean_size=mean_size,
                median_size=median_size,
                size_std=size_std,
                unique_destinations=unique_destinations,
                destination_concentration=destination_concentration,
                interarrival_mean_seconds=interarrival_mean_seconds,
                interarrival_std_seconds=interarrival_std_seconds,
                frequency_spike_score=frequency_spike_score,
                size_spike_score=size_spike_score,
                trend_slope=trend_slope
            )
            db.add(snapshot)
            snapshots_created += 1
            
    db.commit()
    return snapshots_created
