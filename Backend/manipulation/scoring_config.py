WEIGHTS = {
    "normalized_frequency_spike": 0.30,
    "failure_rate": 0.25, # maps to (1 - success_rate)
    "normalized_mean_size": 0.15,
    "normalized_size_volatility": 0.10,
    "normalized_destination_shift": 0.10,
    "normalized_burstiness": 0.10
}

THRESHOLDS = {
    "suspicious": 35.0,
    "manual_review": 70.0
}

REASON_THRESHOLDS = {
    "frequency_spike": 0.7,      # Normalized > 0.7
    "success_rate_min": 0.3,     # Absolute success rate < 0.3
    "mean_size": 0.8,            # Normalized > 0.8
    "destination_shift": 0.6,    # Normalized > 0.6
    "burstiness": 0.7            # Normalized > 0.7
}

REASON_MESSAGES = {
    "frequency_spike": "proposal frequency spike",
    "low_success": "low follow-through rate",
    "large_size": "unusually large average size",
    "destination_change": "sudden destination change",
    "bursty": "bursty repeated behavior"
}
