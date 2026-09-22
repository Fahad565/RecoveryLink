# Development Guide - RecoveryLink

## Local Setup
1. Create virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Copy environment file:
   ```bash
   cp .env.example .env
   ```
3. Run test suite:
   ```bash
   pytest
   ```
4. Start local server:
   ```bash
   uvicorn app.main:app --reload
   ```

## Docker Setup
```bash
docker compose up --build
```
