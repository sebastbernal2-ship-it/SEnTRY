# S.E.N.T.R.Y.

### Secure ENgine for Transaction Risk & Yield‑protection

![Python](https://img.shields.io/badge/python-3.11+-3776AB?logo=python&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-16-000000?logo=nextdotjs&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)
![PyTorch](https://img.shields.io/badge/PyTorch-2.x-EE4C2C?logo=pytorch&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/CI-GitHub_Actions-2088FF?logo=githubactions&logoColor=white)
![Architecture](https://img.shields.io/badge/architecture-serverless-22c55e)
![Status](https://img.shields.io/badge/status-complete-22c55e)

SEnTRY is an AI-driven **security middleware for autonomous on-chain trading agents**. It fuses unsupervised deep learning, behavioral heuristics, NLP signal detection, and on-chain topology analysis into a single **Unified Risk Score (0–100)** that an agent (or a human) can consult before signing a transaction.

The project ships as a completed showcase: a fully decoupled, **serverless** pipeline that runs on GitHub Actions every 10 minutes, writes JSON results into the repository, and is rendered by a Next.js dashboard with first-class sections and custom animations for each risk module.

---

## Table of Contents

- [Why SEnTRY](#why-sentry)
- [Features at a Glance](#features-at-a-glance)
- [System Architecture](#system-architecture)
- [The Four Risk Modules](#the-four-risk-modules)
- [Unified Risk Score](#unified-risk-score)
- [Dashboard](#dashboard)
- [Quick Start](#quick-start)
- [Pipeline & Data Flow](#pipeline--data-flow)
- [JSON Schemas](#json-schemas)
- [Project Structure](#project-structure)
- [Commands Cheatsheet](#commands-cheatsheet)
- [Configuration & Secrets](#configuration--secrets)
- [Notifications](#notifications)
- [Limitations & Future Work](#limitations--future-work)
- [License](#license)

---

## Why SEnTRY

Autonomous trading agents operate 24/7 at machine speed. Without a guard rail, four classes of attack go unnoticed until funds are gone:

1. **Anomalous transactions** that drift from an agent's normal behavioral baseline.
2. **Adversarial counterparties** that gradually manipulate an agent across many small interactions.
3. **Prompt-injection** embedded in agent-to-agent natural language messages.
4. **Money laundering networks** the agent might unknowingly transact with.

SEnTRY is a portfolio-scale demonstration of how each of these can be addressed with a small, transparent stack: a PyTorch autoencoder, heuristic feature engines, NLP scoring, and on-chain topology features — unified behind one risk score and surfaced through a polished dashboard.

---

## Features at a Glance

| Capability | Implementation | Where |
|---|---|---|
| Transaction anomaly detection | PyTorch autoencoder + scaler | `Backend/model/`, `scripts/modules/transaction_anomaly.py` |
| Behavior-based manipulation scoring | Time-series heuristics + reason codes | `scripts/run_monitor.py` (`compute_behavior_manipulation_scores`), `Backend/manipulation/` |
| Prompt-injection / manipulation-signal NLP | Pattern + keyword detection | `scripts/modules/prompt_injection.py` |
| AML / laundering risk | Fan-out, burst, mixer-contact features | `scripts/modules/money_laundering.py` |
| Unified Risk Score | 0–30 / 30–70 / 70–100 banding | `scripts/run_monitor.py`, dashboard |
| Serverless pipeline | GitHub Actions cron (every 10 min) | `.github/workflows/monitor.yml` |
| Dashboard | Next.js 16 + React 19 + Framer Motion | `Frontend/` |
| Module animations | Custom per-module SVG/canvas | `Frontend/components/animations/` |
| Alert deduplication | Hash + TTL state file | `state/already_alerted.json` |
| Notifications | SMTP/SendGrid email, Discord/Slack webhooks | `scripts/utils/notifications.py` |

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Vercel / Local)                │
│  Next.js 16 + React 19 dashboard                            │
│   • Home / Problems / Dashboard / About sections            │
│   • Per-module animations (Anomaly, Behavior, Manipulation, │
│     AML)                                                    │
│   • Fetches static JSON from /data/*.json                   │
└────────────↑────────────────────────────────────────────────┘
             │ fetch /data/*.json (no backend required)
             │
┌────────────┴────────────────────────────────────────────────┐
│         GitHub Repository (the source of truth)             │
│   Frontend/public/data/*.json   ← scored results            │
│   state/already_alerted.json    ← dedup state               │
│   .github/workflows/monitor.yml ← scheduled job             │
└────────────↑────────────────────────────────────────────────┘
             │ commits results every 10 min
             │
┌────────────┴────────────────────────────────────────────────┐
│      GitHub Actions: Analysis Pipeline                      │
│   scripts/run_monitor.py                                    │
│    ├─ Module 1: PyTorch autoencoder (transaction anomalies) │
│    ├─ Module 2: Behavior-manipulation scoring               │
│    ├─ Module 3: NLP prompt-injection detector               │
│    ├─ Module 4: AML topology scorer                         │
│    ├─ Unified Risk Score + alert dedup                      │
│    └─ Notifications (SMTP / SendGrid / webhook)             │
└─────────────────────────────────────────────────────────────┘
```

**Design properties**

- **Serverless by default** — no always-on backend needed for the demo experience.
- **Reproducible** — results are committed to the repo as JSON, so the dashboard is deterministic.
- **Extensible** — every module is a small, isolated Python file with one entry point.
- **Free to host** — Vercel free tier + GitHub Actions free minutes are enough for the 10-minute cadence.

---

## The Four Risk Modules

### Module 1 — Transaction Anomaly Detection
**Method:** PyTorch autoencoder (unsupervised). Learns a behavioral baseline from historical transactions, then flags transactions whose reconstruction error exceeds a threshold.

**Features:** amount, token type, hour, day-of-week, gas fee, address novelty, time since last tx, transaction frequency.

**Code:** `scripts/modules/transaction_anomaly.py`, `Backend/model/autoencoder.py`, `Backend/model/train.py`.

> In CI the autoencoder is opt-in (`ANOMALY_USE_MODEL=true` plus model artifact URLs). Locally it loads by default if `Backend/data/saved_model.pth` and `scaler.pkl` are present; otherwise the module falls back to its heuristic scorer.

### Module 2 — Behavior-Based Manipulation Scoring
**Method:** Time-series heuristics over rolling windows. Computes a 0–100 manipulation score per source by combining anomaly residuals, proposal-frequency spikes, unusual proposal sizes, new-destination behavior, and bursty repetition. Each item carries human-readable **reason codes** explaining the score.

**Code:** `scripts/run_monitor.py` (`compute_behavior_manipulation_scores`) for the CI-friendly path, and the richer feature engine in `Backend/manipulation/feature_engine.py` + `Backend/manipulation/scoring_engine.py` for the standalone service.

### Module 3 — Prompt-Injection & Manipulation-Signal Detection
**Method:** NLP keyword + pattern analysis on agent-to-agent text. Detects urgency cues, false guarantees, FOMO framing, and pressure tactics, returns triggered-pattern lists.

**Code:** `scripts/modules/prompt_injection.py`.

### Module 4 — AML / Counterparty Laundering Risk
**Method:** On-chain topology features per counterparty address — **fan-out** (recipient count), **burst activity** (volume spikes), and **direct mixer contact**. Combined into a single AML risk score with reason codes.

**Code:** `scripts/modules/money_laundering.py`.

---

## Unified Risk Score

Every module emits a 0–100 score plus a label. The dashboard and pipeline use the same banding:

| Score | Label | Recommended action |
|---|---|---|
| 0 – 30 | **Clean** | Auto-approve |
| 30 – 70 | **Suspicious** | Soft-block / human-in-the-loop |
| 70 – 100 | **High Risk** | Hard-block, fire alert |

Scores ≥ 80 produce an alert that is deduplicated against `state/already_alerted.json` before being persisted into `latest-alerts.json` and (optionally) sent to email / webhook channels.

---

## Dashboard

The Next.js frontend is structured as four first-class sections, navigable from the top nav:

- **Home** — animated hero with the project pitch.
- **Problems** — each of the four risk modules gets its own card with a **custom per-module animation** (`AnomalyAnimation`, `BehaviorAnimation`, `ManipulationAnimation`, `AMLAnimation`).
- **Dashboard** — live tables for each module driven by `/data/*.json`: top risk rows, latest scored rows, latest alerts, and module health summary.
- **About** — project context.

A Matrix-style code rain (`MatrixCodeRain`) and pulse beams sit behind everything for the security-console aesthetic. Module scores feed colored severity badges (green / yellow / red) using the same banding as the pipeline.

> **Screenshots / GIFs:** none are checked into the repo yet. To add them, drop image files into `Frontend/public/screenshots/` and reference them here as `![Dashboard](Frontend/public/screenshots/dashboard.png)`. A short Loom or GIF of the Problems section animations would showcase the project well.

---

## Quick Start

### Prerequisites

- **Node.js 18+** (Next.js 16, React 19)
- **Python 3.11+**
- A POSIX shell (Linux / macOS / WSL)

### 1. Clone

```bash
git clone https://github.com/sebastbernal2-ship-it/SEnTRY.git
cd SEnTRY
```

### 2. Run the pipeline once (writes JSON into the frontend's public folder)

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r scripts/requirements-actions.txt

python scripts/run_monitor.py \
  --output-dir Frontend/public/data \
  --state-dir state
```

This generates synthetic transactions, messages, and counterparty addresses, scores them through all four modules, and writes:

```
Frontend/public/data/summary.json
Frontend/public/data/latest-alerts.json
Frontend/public/data/transaction-anomaly.json
Frontend/public/data/behavior-manipulation.json
Frontend/public/data/prompt-injection.json
Frontend/public/data/money-laundering.json
```

### 3. Run the dashboard

```bash
cd Frontend
npm install
npm run dev
# open http://localhost:3000
```

Refresh after re-running the pipeline to pick up new JSON.

---

## Pipeline & Data Flow

The pipeline (`scripts/run_monitor.py`) is the single entry point — locally and in CI. Its flow:

1. **Initialize** the three module detectors (anomaly, prompt injection, AML) and the alert deduplicator.
2. **Generate (or fetch) inputs.** Defaults to synthetic demo data; with `USE_REAL_DATA=true` plus `ALCHEMY_API_KEY` + `TARGET_WALLET_ADDRESS`, the anomaly module ingests real transactions via `Backend/data/ingest.py`. Real-data sources for messages and counterparties are not implemented yet — those modules continue to use synthetic inputs and the README is honest about that.
3. **Score** every input through its module.
4. **Compute Module 2 (behavior manipulation)** from Module 1 outputs using the heuristic scorer baked into `run_monitor.py`. This keeps the pipeline self-contained on CI without needing the standalone `Backend/manipulation` FastAPI service.
5. **Compute summary** (module-level flagged/total counts).
6. **Generate alerts** for any item with score ≥ 80, deduplicated against `state/already_alerted.json`.
7. **Write JSON** into `Frontend/public/data/`.
8. **Send notifications** if email or webhook secrets are configured.
9. **GitHub Actions** then commits the updated JSON + state files back to `main`, which Vercel (or local dev) picks up.

### GitHub Actions workflow

`.github/workflows/monitor.yml`:

- Runs on cron `*/10 * * * *` and on manual `workflow_dispatch`.
- Installs `scripts/requirements-actions.txt`.
- Optionally downloads anomaly model artifacts when `ANOMALY_USE_MODEL=true`.
- Runs `python scripts/run_monitor.py --output-dir Frontend/public/data --state-dir state`.
- Commits and pushes JSON + state changes with message `Update SEnTRY alerts and scores`.

The job uses the built-in `GITHUB_TOKEN`; no extra setup is required to enable the cron.

---

## JSON Schemas

All output files share a `module`, `updated_at`, and `items` shape. Selected examples:

**`summary.json`** — module health snapshot
```json
{
  "updated_at": "2026-05-11T00:00:00Z",
  "scan_status": "ok",
  "modules": [
    { "key": "transaction_anomaly", "title": "Transaction Anomaly Detection", "flagged_count": 2, "total_count": 8 },
    { "key": "behavior_manipulation", "title": "Behavior Manipulation Scoring", "flagged_count": 1, "total_count": 8 },
    { "key": "prompt_injection", "title": "Prompt Injection Detection", "flagged_count": 1, "total_count": 8 },
    { "key": "money_laundering", "title": "Anti-Money Laundering Detection", "flagged_count": 1, "total_count": 8 }
  ]
}
```

**`latest-alerts.json`** — deduplicated alerts (score ≥ 80)
```json
{
  "updated_at": "2026-05-11T00:00:00Z",
  "new_alert_count": 1,
  "alerts": [
    {
      "id": "aml-addr-0001-20260511T000000Z",
      "module": "money_laundering",
      "title": "High-Risk Address Detected",
      "description": "Address 0xDEAD...BEEF shows risky AML patterns (score: 95)",
      "severity": "high",
      "score": 95,
      "label": "High Risk",
      "timestamp": "2026-05-11T00:00:00Z"
    }
  ]
}
```

**`behavior-manipulation.json`** — Module 2 output
```json
{
  "module": "behavior_manipulation",
  "updated_at": "2026-05-11T00:00:00Z",
  "items": [
    {
      "id": "src-tx-0007",
      "source_key": "tx-0007",
      "title": "Behavior Manipulation Risk Detected",
      "risk_score": 78.4,
      "label": "High Risk",
      "severity": "high",
      "reason_codes": ["proposal frequency spike", "new destination behavior"],
      "linked_transaction_id": "tx-0007"
    }
  ]
}
```

`transaction-anomaly.json`, `prompt-injection.json`, and `money-laundering.json` follow the same envelope with module-specific `items`. See `Frontend/lib/api.ts` for the full TypeScript interfaces.

---

## Project Structure

```
SEnTRY/
├── Frontend/                          # Next.js 16 + React 19 dashboard
│   ├── app/                           # App-router entry (page.tsx, layout.tsx)
│   ├── components/
│   │   ├── animations/                # AnomalyAnimation, BehaviorAnimation,
│   │   │                              # ManipulationAnimation, AMLAnimation
│   │   ├── sections/                  # home, problems, dashboard, about
│   │   └── ui/                        # nav, matrix-code-rain, pulse-beams, ...
│   ├── lib/api.ts                     # Typed fetchers for /data/*.json
│   └── public/data/                   # ⭐ Generated JSON results
│
├── Backend/                           # Python ML + optional FastAPI
│   ├── data/                          # ingest.py, generate_data.py, saved_model.pth*
│   ├── model/                         # autoencoder.py, train.py
│   ├── manipulation/                  # standalone behavior service (optional)
│   └── api/                           # FastAPI surface (optional, legacy)
│
├── scripts/                           # ⭐ Pipeline run by GitHub Actions
│   ├── run_monitor.py                 # Main entry point
│   ├── modules/                       # transaction_anomaly, prompt_injection,
│   │                                  # money_laundering
│   ├── utils/                         # io, alerts, scoring, notifications
│   └── requirements-actions.txt
│
├── state/already_alerted.json         # ⭐ Alert dedup state
├── .github/workflows/monitor.yml      # ⭐ Cron pipeline
└── README.md
```

⭐ Files central to the serverless architecture.

---

## Commands Cheatsheet

| Action | Command |
|---|---|
| Install pipeline deps | `pip install -r scripts/requirements-actions.txt` |
| Run pipeline (demo data) | `python scripts/run_monitor.py --output-dir Frontend/public/data --state-dir state` |
| Run pipeline (real tx data) | `USE_REAL_DATA=true python scripts/run_monitor.py --output-dir Frontend/public/data --state-dir state` |
| Install frontend deps | `cd Frontend && npm install` |
| Start dashboard (dev) | `cd Frontend && npm run dev` |
| Build dashboard (prod) | `cd Frontend && npm run build && npm run start` |
| Lint frontend | `cd Frontend && npm run lint` |
| Install full backend env | `cd Backend && pip install -r requirements.txt` |
| Train autoencoder | `cd Backend && python model/train.py` |
| Ingest real tx history | `cd Backend && python data/ingest.py` |
| Run optional FastAPI server | `cd Backend && python api/main.py` |

---

## Configuration & Secrets

All secrets are optional — the demo runs without any of them.

### Local development (`Backend/.env`)
Copy `Backend/.env.example` to `Backend/.env` and set:
```
ALCHEMY_API_KEY=your_alchemy_api_key
TARGET_WALLET_ADDRESS=0x...
ALCHEMY_NETWORK=eth-mainnet
USE_REAL_DATA=True
```

### GitHub Actions secrets

| Secret | Purpose |
|---|---|
| `USE_REAL_DATA` | `true` to attempt real-data ingestion in CI |
| `ALCHEMY_API_KEY` | Alchemy RPC key (Module 1 real-data path) |
| `TARGET_WALLET_ADDRESS` | Wallet to monitor |
| `ANOMALY_USE_MODEL` | `true` to load the trained autoencoder in CI |
| `ANOMALY_MODEL_URL` / `ANOMALY_SCALER_URL` | Authenticated download URLs for `saved_model.pth` and `scaler.pkl` |
| `SENTRY_EMAIL_PROVIDER` | `smtp` or `sendgrid` |
| `SENTRY_SMTP_*` | `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD` |
| `SENTRY_SENDGRID_API_KEY` | SendGrid API key (alternative to SMTP) |
| `SENTRY_EMAIL_FROM` / `SENTRY_EMAIL_TO` | Email addresses |
| `SENTRY_WEBHOOK_URL` | Discord / Slack incoming webhook |

---

## Notifications

`scripts/utils/notifications.py` ships two backends:

- **Email** — SMTP (Gmail app password, etc.) or SendGrid. Triggered when `SENTRY_EMAIL_PROVIDER` plus the matching credentials are set.
- **Webhook** — POSTs an alert payload to `SENTRY_WEBHOOK_URL`. Compatible with Discord and Slack incoming webhooks.

Alerts are produced from any module item with `risk_score ≥ 80` and a severity of `high`. The deduplicator (`scripts/utils/alerts.py`) hashes `(module, entity_id, severity)` and stores it in `state/already_alerted.json` with a 24-hour TTL so the same alert never fires twice per window.

---

## Limitations & Future Work

This is a portfolio showcase. The honest current state:

- **Demo-first inputs.** Modules 2, 3, and 4 are driven by synthetic inputs in CI. Only Module 1 has a real-data path (Alchemy → `Backend/data/ingest.py`). Hooking real message streams and real counterparty lists into Modules 3 & 4 is the obvious next step.
- **Autoencoder thresholding.** The reconstruction-error threshold is heuristic. A calibrated per-wallet threshold would reduce false positives on noisy wallets.
- **Behavior manipulation in CI is a reduced model.** The richer `Backend/manipulation` service (FastAPI + SQLite + classifier) is included but not wired into the GitHub Actions cron to keep CI hermetic.
- **No production integrations.** SEnTRY is not deployed against any live trading agent. The dashboard reflects pipeline output committed to the repo — there is no live blockchain stream, no live agent bus, and no upstream OAuth/identity layer.
- **Frontend assets.** Screenshots / GIFs are not yet checked in. Adding them under `Frontend/public/screenshots/` would significantly improve the GitHub landing experience.
- **Test coverage.** Unit tests exist for parts of `Backend/manipulation` but not yet for `scripts/modules/`. A small pytest suite covering the four module entry points would be high-value follow-up work.

### Roadmap ideas
- Real-data adapters for Modules 3 (LLM message bus) and 4 (chain-analytics API).
- Per-wallet adaptive thresholds for the autoencoder.
- Replace the in-`run_monitor.py` behavior heuristic with the full `Backend/manipulation` classifier in CI.
- Dashboard time-series charts (24h / 7d trends) backed by historical JSON snapshots.
- Pytest + GitHub Actions test job.

---

## License

No license file is currently included. Add a `LICENSE` (MIT recommended for a portfolio project) before publishing.

---

## Acknowledgements

Built around PyTorch, scikit-learn, Next.js, React 19, Framer Motion, and Tailwind. Hosted via GitHub Actions + Vercel free tiers.
