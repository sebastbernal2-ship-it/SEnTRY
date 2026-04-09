# Behavior-Based Manipulation Scoring

This is the manipulation scoring capability for SEnTRY. This standalone service enables tracking external agents or data sources over time, computing behavior features, assigning manipulation risk scores, and generating explainable alerts.

## Milestone 1 Setup

### 1. Configure Environment
Ensure you have Python 3.9+ installed.

### 2. Install Dependencies
Navigate to the `manipulation` directory:
```bash
cd Backend/manipulation
pip install -r requirements.txt
```

### 3. Initialize the Database and Seed
Run the seed script. This will automatically create the `manipulation.db` SQLite database and initialize all the schema tables.
```bash
python -m manipulation.seed
```

### 4. Run the API Server
Start the FastAPI server locally:
```bash
uvicorn manipulation.main:app --reload
```

### 5. Verify Health
Navigate to `http://127.0.0.0:8000/health` (or `http://localhost:8000/health`) to confirm the API is running and connected to the SQLite database.
