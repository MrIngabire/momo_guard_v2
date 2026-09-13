# MoMo Guard — Backend & Analyst Console

Hybrid ML + LLM smishing detection system for MTN Rwanda Mobile Money.

This repo contains the **FastAPI backend** and the **React analyst dashboard**.
The native Android edge client lives in a separate repository.

## Architecture

- **Backend** — FastAPI + PostgreSQL, JWT auth, ML (RandomForest) + Gemini fallback
- **Frontend** — React + Vite analyst console with role-based access
- **ML** — TF-IDF vectorization, hybrid 3-tier classification (Safe / Suspicious / Scam)

## Setup

### Backend

```bash
cd backend
python -m venv ../.venv
../.venv/Scripts/Activate.ps1       # Windows PowerShell
pip install -r requirements.txt
cp .env.example .env                # then fill in the values
python -m app.seed                  # creates admin + analyst users
uvicorn app.main:app --reload --port 8000
```

- API docs: http://localhost:8000/docs
- Seed users:
  - `admin@momoguard.rw` / `Admin@1234`
  - `analyst@momoguard.rw` / `Analyst@1234`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173.

## Endpoints

| Method | Path | Auth | Notes |
|---|---|---|---|
| POST | `/api/auth/login` | — | JWT login |
| POST | `/api/auth/register` | — | create user |
| GET | `/api/auth/me` | JWT | current user |
| POST | `/api/scan` | JWT | scan + log |
| POST | `/api/scan-public` | — | scan from mobile app |
| POST | `/api/feedback` | JWT | mark false positive |
| GET | `/api/dashboard` | JWT | aggregate stats |
| GET | `/api/scans` | JWT | full history |
| GET | `/api/users` | admin | user list |
| PATCH | `/api/users/{id}` | admin | role / disable |
| DELETE | `/api/users/{id}` | admin | delete |
| POST | `/api/retrain` | admin | retrain ML |
| GET | `/api/audit-logs` | admin | audit trail |
| GET | `/api/health` | JWT | health + metrics |
| GET | `/api/metrics` | JWT | ML metrics |

## Stack

- Python 3.12, FastAPI, SQLAlchemy, PostgreSQL 18
- React 18, Vite 5, Recharts
- scikit-learn (RandomForest), TF-IDF
- Google Gemini 2.5 Flash (fallback)