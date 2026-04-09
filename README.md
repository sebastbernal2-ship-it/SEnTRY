# S.E.N.T.R.Y.
### Secure ENgine for Transaction Risk & Yield‑protection

SEnTRY is an AI-driven security middleware designed to safeguard autonomous crypto-trading agents. By operating as a persistent guard rail between trading bots and the blockchain, SEnTRY enforces user-defined policies and employs machine learning to intercept manipulative tactics, behavioral anomalies, and money laundering attempts in real time.

---

## The Problem
The growth of autonomous trading agents has introduced a new class of systemic risks. Trading bots are frequently targeted by sophisticated manipulation attempts—such as predatory trade sizing, contract exploitation, and social engineering through agent-to-agent communication—designed to induce sub-optimal execution. Furthermore, the lack of automated AML (Anti-Money Laundering) verification at the point of trade execution leaves agents vulnerable to interacting with high-risk or sanctioned clusters.

## The Solution
SEnTRY provides a comprehensive security dashboard and API layer that scores each proposed transaction across four specialized intelligence modules. The system generates a Unified Risk Score (0-100) that allows users to define automated block/flagging policies, ensuring that only verified, non-manipulative transactions reach the blockchain.

---

## Core Security Pillars

### 1. Transaction Anomaly Detection (Core ML)
An unsupervised Autoencoder model that establishes a behavioral baseline for the user's agent. By learning standard patterns of trade size, token preference, and execution timing, the model flags transactions that deviate significantly from historical data as potential breaches or exploits.

### 2. Behavior-Based Manipulation Scoring
Led by **Sebastian**, this module monitors the behavior of external data sources and counterparties. It tracks time-series features such as proposal frequency and success rates to identify high-volume, predatory agents attempting to manipulate market prices or induce bad trades.

### 3. NLP Manipulation & Signal Detection
Led by **Brian**, this module employs Natural Language Processing to analyze agent-to-agent communications. It identifies manipulative language, high-pressure urgency cues, and potential prompt-injection attempts used to deceive automated trading strategies.

### 4. Money Laundering Detector
Led by **Nicolas**, this module scores counterparty addresses for AML risk. It analyzes on-chain topology (fan-out structures, mixer proximity, and burst activity) to calculate the probability that a destination address is part of a laundering pattern or high-risk cluster.

---

## Unified Risk Engine
SEnTRY aggregates signals from all four modules into a single, actionable risk index:
* **0–30: Auto-Approve** – Low risk, standard execution.
* **30–70: Soft-Block** – Requires manual confirmation or additional agent verification.
* **70–100: Critical Block** – High probability of manipulation or breach; transaction is intercepted.

---

## Technology Stack
* **Intelligence Layer**: PyTorch (Autoencoder & ML Classifiers)
* **API Middleware**: FastAPI (High-concurrency risk scoring)
* **Blockchain Data**: Alchemy (Real-time on-chain ledger ingestion)
* **Dashboard**: Next.js (Cyber-aesthetic monitoring interface)

---

## Project Structure
```
SEnTRY/
├── Frontend/    # Next.js Dashboard & UI
└── Backend/     # FastAPI, PyTorch Model, & Alchemy Pipelines
```

## Setup and Deployment
1. **Configure Environment**: Set `ALCHEMY_API_KEY` and `TARGET_WALLET_ADDRESS` in `Backend/.env`.
2. **Data Ingestion**: Run `python Backend/data/ingest.py` to build the wallet baseline.
3. **Model Training**: Run `python Backend/model/train.py` to initialize the behavioral DNA.
4. **API Standup**: Run `python Backend/api/main.py`.
5. **Dashboard**: Run `npm run dev` within the `Frontend` directory.
