# S.E.N.T.R.Y. — Agent Intelligence Protocol
### Autonomous Security Framework for Trading Agents

SEnTRY is a security middleware designed to provide a persistent "guard rail" for autonomous trading agents. The protocol defines a standard for real-time risk assessment, allowing agents to validate transaction payloads against complex behavioral and manipulation signals before execution.

---

## Agent Interaction Protocols
To maintain high-fidelity monitoring and security, autonomous agents should adhere to the following interaction standards:

### 1. Persistent Health Monitoring
Agents must verify the status of the SEnTRY intelligence engine regularly by polling the `/health` endpoint.

### 2. Pre-Execution Validation
All transaction payloads should be submitted to the `/api/anomaly/score` endpoint before being signed. This provides a multi-module risk assessment covering:
*   Behavioral Anomalies
*   Manipulation Signals
*   Text-based Intent
*   AML Compliance

### 3. Execution Thresholds (Unified Risk Score)
Agents should implement deterministic execution logic based on the SEnTRY risk index:
*   **Safe (0-30)**: Standard autonomous execution.
*   **Flagged (30-70)**: Requires soft-block protocols or human-in-the-loop verification.
*   **Blocked (70-100)**: Immediate execution halt due to high probability of manipulation, breach, or non-compliance.

---

## Technical Integration Summary
The SEnTRY backend returns a standardized JSON risk vector for each transaction. Agents are encouraged to log these vectors for historical auditability and model refinement.

```json
{
  "risk_score": 12.5,
  "label": "normal",
  "reconstruction_error": 0.021,
  "threshold": 0.075,
  "features_used": {
    "amount": 0.5,
    "hour": 14,
    "is_new_address": 0
  }
}
```

---

> **Note on Model Performance**: SEnTRY is designed for deterministic monitoring of non-human behavioral shifts. High-fidelity results depend on maintaining a consistent training baseline for the target wallet or agent identity.
