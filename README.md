# S.E.N.T.R.Y.
### Secure ENgine for Transaction Risk & Yield‑protection

SEnTRY is an AI-driven security middleware designed to safeguard autonomous crypto-trading agents. It employs machine learning and heuristic analysis to intercept manipulative tactics, behavioral anomalies, and money laundering attempts.

**New 2026 Architecture**: SEnTRY now runs as a fully decoupled system—the frontend lives on Vercel, while the analysis pipeline executes on a schedule via GitHub Actions. No always-on backend required.

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Vercel)                        │
│  Next.js Dashboard → Fetches JSON from public/data/         │
└────────────↑────────────────────────────────────────────────┘
             │ (reads /data/*.json)
             │
┌────────────┴────────────────────────────────────────────────┐
│         GitHub (Repository)                                  │
│  ┌─ Frontend/public/data/ (JSON results)                    │
│  ├─ state/already_alerted.json (deduplication state)        │
│  └─ .github/workflows/monitor.yml (scheduled analysis)      │
└────────────↑────────────────────────────────────────────────┘
             │ (writes results every 10 min)
             │
┌────────────┴────────────────────────────────────────────────┐
│      GitHub Actions (Analysis Pipeline)                     │
│  runs: scripts/run_monitor.py                               │
│  ├─ PyTorch Autoencoder (transaction anomalies)             │
│  ├─ NLP Scoring (prompt injection)                          │
│  ├─ AML Scoring (money laundering)                          │
│  └─ Alert Deduplication & Notifications                     │
└─────────────────────────────────────────────────────────────┘
```

**Key Properties:**
- ✅ **Serverless by default** – No always-on backend host
- ✅ **ML-native** – PyTorch Autoencoder, scikit-learn classifiers
- ✅ **Fully reproducible** – Results cached in JSON, history preserved
- ✅ **Alert deduplication** – No duplicate alerts across runs
- ✅ **Extensible notifications** – Email, webhooks (Discord, Slack, etc.)
- ✅ **Free** – GitHub Actions + Vercel free tier

---

## 🔧 Core Security Modules

### Module 1: Transaction Anomaly Detection
**Method**: PyTorch Autoencoder (unsupervised learning)

Learns behavioral baseline from historical transactions. Flags transactions that deviate significantly from this baseline as potential breaches or exploits.

**Features analyzed:**
- Transaction amount
- Token type
- Time of day & day of week
- Gas fee
- Address novelty
- Inter-transaction timing
- Transaction frequency

**Model**: `Backend/data/saved_model.pth`, trained via `Backend/model/train.py`

---

### Module 2: Behavior-Based Manipulation Scoring
**Method**: Time-series heuristics + historical aggregation

Monitors external agent behavior over rolling windows (1h, 6h, 24h). Calculates proposal frequency spikes, success rates, and mean transaction sizes to identify predatory patterns.

**Detector**: `Backend/manipulation/feature_engine.py` + ML classifier

---

### Module 3: Prompt Injection & Text Manipulation
**Method**: NLP keyword detection + pattern analysis

Analyzes agent-to-agent communication for:
- Urgency language ("NOW", "IMMEDIATELY", "expires in")
- Guaranteed claims ("GUARANTEED", "risk-free")
- FOMO tactics ("act before", "last chance")
- Pressure tactics

**Detector**: `scripts/modules/prompt_injection.py`

---

### Module 4: Anti-Money Laundering (AML)
**Method**: On-chain topology scoring

Scores counterparty addresses for AML risk:
- **Fan-out patterns**: Number of recipients (high = riskier)
- **Burst activity**: Sudden spikes in transaction volume
- **Mixer contact**: Direct interaction with known mixing services

**Detector**: `scripts/modules/money_laundering.py`

---

## 📊 Unified Risk Engine

All four modules feed into a **Unified Risk Score (0–100)**:

| Score Range | Label | Action |
|---|---|---|
| 0–30 | **Clean** | Auto-approve ✅ |
| 30–70 | **Suspicious** | Soft-block ⚠️ |
| 70–100 | **High Risk** | Critical block 🚫 |

Dashboard displays module-level scores, latest alerts, and historical trends.

---

## 🚀 Getting Started

### Prerequisites
- **Frontend**: Node.js 18+ (npm)
- **Backend**: Python 3.11+
- **Deployment**: GitHub + Vercel accounts (free tier OK)

### Local Setup

#### 1. Clone and install frontend
```bash
cd Frontend
npm install
npm run dev
# Opens http://localhost:3000
```

#### 2. Set up Python environment
```bash
cd ../Backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
```

#### 3. Prepare data (optional - for real API testing)
```bash
# Configure .env for real API keys:
# ALCHEMY_API_KEY=your_key
# TARGET_WALLET_ADDRESS=0x...

# Ingest transaction history
python data/ingest.py

# Train anomaly model (optional if using existing saved_model.pth)
python model/train.py
```

#### 4. Test the analysis pipeline locally
```bash
cd ../
python SEnTRY/scripts/run_monitor.py \
  --output-dir ./SEnTRY/Frontend/public/data \
  --state-dir ./SEnTRY/state
```

The script will:
1. Generate demo transaction/message/address data
2. Run all four analysis modules
3. Write JSON results to `Frontend/public/data/`
4. Track which alerts have been sent to avoid duplicates

#### 5. Reload frontend
Navigate to http://localhost:3000 (refresh if already open). The dashboard now displays live data from the JSON files.

---

## 📋 Data Flow & JSON Schemas

### Output Files (Generated by Analysis Pipeline)

**`public/data/summary.json`** – Module health snapshot
```json
{
  "updated_at": "2026-04-13T22:00:00Z",
  "scan_status": "ok",
  "modules": [
    {
      "key": "transaction_anomaly",
      "title": "Transaction Anomaly Detection",
      "flagged_count": 2,
      "total_count": 8
    }
  ]
}
```

**`public/data/latest-alerts.json`** – Real-time alerts for frontend display
```json
{
  "updated_at": "2026-04-13T22:00:00Z",
  "new_alert_count": 2,
  "alerts": [
    {
      "id": "aml-0xDEAD...BEEF-20260413T215800Z",
      "module": "money_laundering",
      "title": "High-risk laundering pattern detected",
      "description": "Address 0xDEAD...BEEF shows mixer contact + burst activity",
      "severity": "high",
      "score": 95,
      "label": "High Risk",
      "timestamp": "2026-04-13T21:58:00Z"
    }
  ]
}
```

**`public/data/transaction-anomaly.json`** – All transaction scores
```json
{
  "module": "transaction_anomaly",
  "updated_at": "2026-04-13T22:00:00Z",
  "items": [
    {
      "id": "tx-0001",
      "amount": 1.5,
      "risk_score": 12,
      "label": "Clean",
      "severity": "low"
    }
  ]
}
```

**`public/data/prompt-injection.json`** – All message scores
```json
{
  "module": "prompt_injection",
  "updated_at": "2026-04-13T22:00:00Z",
  "items": [
    {
      "id": "msg-0001",
      "preview": "Swap 0.5 ETH to USDC at market rate.",
      "risk_score": 5,
      "label": "Clean"
    }
  ]
}
```

**`public/data/money-laundering.json`** – All address scores
```json
{
  "module": "money_laundering",
  "updated_at": "2026-04-13T22:00:00Z",
  "items": [
    {
      "id": "addr-0001",
      "address": "0xDEAD...BEEF",
      "fan_out": "Very High",
      "burst_activity": true,
      "mixer_contact": true,
      "risk_score": 95,
      "label": "High Risk"
    }
  ]
}
```

---

## 🔄 GitHub Actions Workflow

**File**: `.github/workflows/monitor.yml`

**Triggers:**
- **Scheduled**: Every 10 minutes (configurable via `cron` in workflow)
- **Manual**: Click "Run workflow" in GitHub Actions tab

**What it does:**
1. Checks out code
2. Sets up Python 3.11
3. Installs dependencies from `scripts/requirements-actions.txt`
4. Runs `scripts/run_monitor.py`
5. If JSON or state files changed, commits & pushes them back to `main`

**Preventing infinite loops:**
- Workflow only triggered by scheduled/manual events, not by bot commits
- Uses `GITHUB_TOKEN` (built-in, no setup needed)

---

## 🔔 Alert Deduplication & Notifications

### Deduplication (State Management)

`state/already_alerted.json` tracks which alerts have been sent:
```json
{
  "a1b2c3d4e5f6g7h8": "2026-04-13T21:58:00Z",
  "transaction_anomaly:tx-0001:high": "2026-04-13T20:00:00Z"
}
```

**TTL**: By default, alerts are "forgotten" after 24 hours (configurable).

### Sending Notifications

The pipeline can send alerts via **email** and **webhooks**.

#### Email (Optional)
Set these GitHub Actions secrets to enable email alerts:
- `SENTRY_EMAIL_PROVIDER` – `"smtp"` (default) or `"sendgrid"`
- `SENTRY_SMTP_HOST` – e.g., `smtp.gmail.com`
- `SENTRY_SMTP_PORT` – e.g., `587`
- `SENTRY_SMTP_USER` – your email
- `SENTRY_SMTP_PASSWORD` – your app password (not real password)
- `SENTRY_EMAIL_FROM` – sender email
- `SENTRY_EMAIL_TO` – recipient(s), comma-separated

Or use SendGrid:
- `SENTRY_EMAIL_PROVIDER` – `"sendgrid"`
- `SENTRY_SENDGRID_API_KEY` – your SendGrid API key

#### Webhooks (Discord, Slack, etc.)
Set:
- `SENTRY_WEBHOOK_URL` – webhook endpoint URL

Example Discord webhook setup:
1. Go to your Discord server settings → Integrations → Webhooks
2. Create a new webhook
3. Copy the webhook URL
4. Add as GitHub Actions secret `SENTRY_WEBHOOK_URL`

---

## 📁 Project Structure

```
SEnTRY/
├── Frontend/                    # Next.js dashboard (Vercel)
│   ├── app/
│   │   ├── page.tsx            # Main page
│   │   └── layout.tsx
│   ├── components/
│   │   ├── sections/
│   │   │   └── dashboard.tsx   # Fetches from /data/*.json
│   │   └── ui/
│   ├── lib/
│   │   └── api.ts              # JSON fetch functions
│   ├── public/
│   │   └── data/               # Generated JSON results ⭐
│   │       ├── summary.json
│   │       ├── latest-alerts.json
│   │       ├── transaction-anomaly.json
│   │       ├── prompt-injection.json
│   │       └── money-laundering.json
│   └── package.json
│
├── Backend/                     # Python ML & data processing
│   ├── data/
│   │   ├── saved_model.pth     # Trained autoencoder
│   │   ├── scaler.pkl          # Feature scaler
│   │   └── transactions.csv
│   ├── model/
│   │   ├── autoencoder.py
│   │   └── train.py
│   ├── manipulation/           # Behavior-based scoring
│   │   ├── database.py
│   │   ├── feature_engine.py
│   │   └── main.py
│   ├── api/                    # FastAPI endpoints (legacy/optional)
│   │   ├── main.py
│   │   ├── scorer.py
│   │   └── manipulation_scorer.py
│   └── requirements.txt
│
├── scripts/                    # Analysis pipeline ⭐
│   ├── run_monitor.py          # Main entry point
│   ├── requirements-actions.txt
│   ├── utils/
│   │   ├── io.py              # JSON helpers
│   │   ├── alerts.py          # Deduplication
│   │   ├── scoring.py         # Common scoring utils
│   │   └── notifications.py   # Email/webhooks
│   └── modules/
│       ├── transaction_anomaly.py
│       ├── prompt_injection.py
│       └── money_laundering.py
│
├── state/                      # Persistent state ⭐
│   └── already_alerted.json    # Deduplication tracker
│
├── .github/workflows/
│   └── monitor.yml             # GitHub Actions workflow ⭐
│
└── README.md (this file)
```

⭐ = Key files for new architecture

---

## 🔐 Secrets & Environment Variables

### GitHub Actions Secrets (for CI/CD)
Add these via GitHub → Settings → Secrets and variables → Actions:

**For data ingestion** (if using real APIs):
- `ALCHEMY_API_KEY` – Alchemy RPC key
- `TARGET_WALLET_ADDRESS` – Wallet to monitor

**For email notifications**:
- `SENTRY_EMAIL_PROVIDER` – `"smtp"` or `"sendgrid"`
- `SENTRY_SMTP_HOST`, `SENTRY_SMTP_PORT`, `SENTRY_SMTP_USER`, `SENTRY_SMTP_PASSWORD`
- Or `SENTRY_SENDGRID_API_KEY`
- `SENTRY_EMAIL_FROM`, `SENTRY_EMAIL_TO`

**For webhooks**:
- `SENTRY_WEBHOOK_URL` – Discord/Slack webhook endpoint

### Local `.env` Files (for development)
Create `Backend/.env`:
```
ALCHEMY_API_KEY=sk_eth_...
TARGET_WALLET_ADDRESS=0x...
```

---

## 🛠️ Extending the System

### Adding a New Analysis Module

1. **Create module** (e.g., `scripts/modules/compliance_checker.py`):
```python
class ComplianceChecker:
    def score_transaction(self, tx):
        # Your logic here
        return {"risk_score": 45, "label": "Suspicious", ...}
```

2. **Update pipeline** (`scripts/run_monitor.py`):
```python
from modules.compliance_checker import ComplianceChecker

checker = ComplianceChecker()
compliance_scores = [checker.score_tx(tx) for tx in transactions]
```

3. **Write JSON output**:
```python
write_json(
    os.path.join(output_dir, "compliance.json"),
    {"module": "compliance", "updated_at": get_utc_now(), "items": compliance_scores}
)
```

4. **Update frontend** (`Frontend/lib/api.ts`) to fetch the new JSON file.

### Using Real Data Instead of Demo Data

1. **Load data** in `scripts/run_monitor.py`:
```python
# Instead of: anomaly_transactions = anomaly_detector.generate_demo_transactions(8)
anomaly_transactions = load_transactions_from_api()  # your function
```

2. **Pass `--use-real-data` flag**:
```bash
python scripts/run_monitor.py --use-real-data
```

### Changing Workflow Schedule

Edit `.github/workflows/monitor.yml`:
```yaml
schedule:
  - cron: '*/5 * * * *'  # Every 5 minutes instead of 10
```

---

## 📊 Monitoring & Debugging

### Check Workflow Runs
1. Go to GitHub repo → Actions tab
2. Click "S.E.N.T.R.Y. Monitoring Pipeline" workflow
3. View run history and logs

### Local Testing
```bash
cd SEnTRY
python scripts/run_monitor.py --output-dir ./Frontend/public/data --state-dir ./state
cat Frontend/public/data/summary.json
```

### Inspect State
```bash
cat state/already_alerted.json
```

### Verify Frontend Fetching
Open browser DevTools (F12) → Network tab → Reload. Should see fetches for:
- `/data/summary.json`
- `/data/latest-alerts.json`
- `/data/transaction-anomaly.json`
- `/data/prompt-injection.json`
- `/data/money-laundering.json`

---

## 🚢 Deployment

### Frontend (Vercel)
1. Push `Frontend/` to GitHub repo
2. Connect repo to Vercel (https://vercel.com/import)
3. Vercel auto-detects Next.js and deploys
4. Set environment variables if needed (for APIs, etc.)

### Analysis Pipeline (GitHub Actions)
- **Automatic**: Workflow defined in `.github/workflows/monitor.yml`
- **No setup required**: Uses built-in GitHub Actions runner
- **Runs every 10 minutes**: Configurable in workflow YAML

### Backend (Optional for Real APIs)
If you want a live API for real-time scoring:
```bash
cd Backend
python api/main.py
# Runs on http://localhost:8000
```
Deploy to your own server (DigitalOcean, AWS, etc.) or use Render/Railway (for hobby projects).

---

## 📈 Performance & Costs

| Component | Cost | Notes |
|---|---|---|
| **Frontend** | Free | Vercel free tier (up to 100GB/month) |
| **GitHub Actions** | Free | 2,000 free minutes/month (more than enough for 10-min intervals) |
| **Email Notifications** | $$ | SendGrid free tier: 100 emails/day |
| **Blockchain Data** | $ | Alchemy free tier: up to 3M cu/month |
| **Total** | **Free–$50/mo** | Depending on data volume |

---

## 🐛 Troubleshooting

### Workflow not triggering
- Check `.github/workflows/monitor.yml` syntax (GitHub validates on push)
- Verify cron schedule is correct (https://crontab.guru/)
- Check Actions tab for error logs

### JSON files not updating
- Check Actions tab for workflow failures
- Verify `Frontend/public/data/` directory exists
- Check git push permissions (should be automatic with `GITHUB_TOKEN`)

### Frontend shows stale data
- Hard refresh: `Ctrl+Shift+R` (or `Cmd+Shift+R` on macOS)
- Check browser cache → DevTools → Network → Disable cache

### Email not sending
- Verify credentials in GitHub Actions secrets
- Try sending a test email locally: 
  ```python
  from scripts.utils.notifications import EmailNotificationService
  service = EmailNotificationService()
  service.send_alert_email({...})
  ```

---

## 📚 API Reference

### `scripts/run_monitor.py`
Entry point for the analysis pipeline.

**Options:**
- `--output-dir DIR` – Where to write JSON files (default: `./Frontend/public/data`)
- `--state-dir DIR` – Where to store deduplication state (default: `./state`)
- `--use-real-data` – Use real data instead of demo data

**Returns JSON:**
```json
{
  "status": "success",
  "new_alerts": 2,
  "anomalies_scored": 8,
  "messages_scored": 8,
  "addresses_scored": 8,
  "output_dir": "./Frontend/public/data"
}
```

### Frontend API (`Frontend/lib/api.ts`)

#### `getSummary(): Promise<Summary>`
Fetch module health snapshot.

#### `getLatestAlerts(): Promise<Alert[]>`
Fetch latest alerts (for alert banner).

#### `getTransactionAnomalies(): Promise<AnomalyItem[]>`
Fetch all transaction anomaly scores.

#### `getPromptInjectionData(): Promise<TextItem[]>`
Fetch all text/message scores.

#### `getMoneyLaunderingData(): Promise<AMLItem[]>`
Fetch all address AML scores.

---

## 📄 License

[Your License Here]

---

## 💬 Support

For issues, feature requests, or questions:
- Open a GitHub issue
- Check documentation above
- Email: sentry@project.local

---

**Last Updated**: April 13, 2026
**Version**: 2.0 (Serverless Architecture)
├── Frontend/    # Next.js Dashboard & UI
└── Backend/     # FastAPI, PyTorch Model, & Alchemy Pipelines
```

## Setup and Deployment
1. **Configure Environment**: Set `ALCHEMY_API_KEY` and `TARGET_WALLET_ADDRESS` in `Backend/.env`.
2. **Data Ingestion**: Run `python Backend/data/ingest.py` to build the wallet baseline.
3. **Model Training**: Run `python Backend/model/train.py` to initialize the behavioral DNA.
4. **API Standup**: Run `python Backend/api/main.py`.
5. **Dashboard**: Run `npm run dev` within the `Frontend` directory.
