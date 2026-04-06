# S.E.N.T.R.Y.
### Secure ENgine for Transaction Risk & Yield-protection

> An AI-powered security layer that sits between your crypto trading agent and the blockchain — detecting manipulation, anomalous transactions, and money laundering patterns in real time.

---

## 📁 Project Structure
```
SEnTRY/
├── Frontend/    ← Next.js web app
└── Backend/     ← Python FastAPI + PyTorch ML
```

---

## 🚀 Getting Started

You'll need **two terminals open simultaneously** — one for the frontend, one for the backend.

---

## 🖥️ Frontend
```bash
cd Frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

---

## ⚙️ Backend

### 1. Create & activate a virtual environment
```bash
cd Backend
py -3.11 -m venv venv
```

**Windows PowerShell:**
```powershell
venv\Scripts\activate
```

**Git Bash:**
```bash
source venv/Scripts/activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Generate synthetic data
```bash
python data/generate_data.py
```

### 4. Train the model
```bash
cd model
python train.py
```

### 5. Start the API
```bash
cd ../api
python main.py
```

- API: [http://localhost:8000](http://localhost:8000)
- Interactive docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 👥 Team

| Name |
|------|
| Nicolas |
| Sebastian |
| Dario |
