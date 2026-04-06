# S.E.N.T.R.Y.
Secure ENgine for Transaction Risk & Yield-protection

An AI-powered security layer that sits between your crypto trading agent and the blockchain, detecting manipulation, anomalous transactions, and money laundering patterns in real time.

---

## Project Structure

\```
SEnTRY/
├── Frontend/    ← Next.js web app
└── Backend/     ← Python FastAPI + PyTorch ML
\```

---

## Running the Frontend

\```bash
cd Frontend
npm install
npm run dev
\```

Open `http://localhost:3000`

---

## Running the Backend

**1. Create and activate virtual environment**

\```bash
cd Backend
py -3.11 -m venv venv
\```

Windows PowerShell:
\```bash
venv\Scripts\activate
\```

Git Bash:
\```bash
source venv/Scripts/activate
\```

**2. Install dependencies**

\```bash
pip install -r requirements.txt
\```

**3. Generate synthetic data**

\```bash
python data/generate_data.py
\```

**4. Train the model**

\```bash
cd model
python train.py
\```

**5. Start the API**

\```bash
cd ../api
python main.py
\```

API runs at `http://localhost:8000`

Interactive docs at `http://localhost:8000/docs`

---

## Running Both Together

You need two terminals open at the same time — one for the frontend and one for the backend.

---

## Team

Nicolas, Sebastian, Dario
