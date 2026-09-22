# 🛡️ RecoveryLink

### Digital Recovery Through the Mobile Network

> **Prepare. Protect. Recover.**

RecoveryLink is a telecom-accessible digital recovery platform built for Africa's Talking hackathon that allows users to perform safety checks, track readiness scores, manage recovery profiles, and receive instant emergency recovery plans via SMS using USSD menu interactions.

## Architecture & Structure

```text
RecoveryLink/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── api/
│   ├── services/
│   ├── models/
│   └── database/
├── docs/
│   ├── PRD.md
│   ├── ARCHITECTURE.md
│   ├── DEVELOPMENT.md
│   └── SESSION_HANDOFF.md
├── tests/
├── Dockerfile
├── docker-compose.yml
├── render.yaml
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Quick Start

### 1. Environment Setup
```bash
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Run Application
```bash
uvicorn app.main:app --reload
```
Visit http://localhost:8000/docs for interactive API documentation.

### 3. Docker
```bash
docker compose up --build
```
