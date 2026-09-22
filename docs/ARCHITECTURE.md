# Technical Architecture - RecoveryLink

## System Diagram
```text
                    USER
                      │
                      ▼
               USSD / SMS HTTP
                      │
                      ▼
             AFRICA'S TALKING
                      │
                      ▼
             FASTAPI APP (Router)
                      │
      ┌───────────────┼───────────────┐
      ▼               ▼               ▼
USSD Engine     Readiness &      Messaging &
 (Stateful)     Recovery Svc       AI Layer
      │               │               │
      └───────────────┼───────────────┘
                      ▼
                 DATABASE (SQLite/PostgreSQL)
```

## Core Components
1. **FastAPI Web Router**: Handles USSD callback, SMS webhooks, health checks, and API endpoints.
2. **USSD Session State Engine**: Parses concatenated user input (`text=1*2*1`) into navigation hops and updates database state.
3. **Readiness Engine**: Computes scores (0-100) based on weighted safety parameters.
4. **AI & Messaging Layer**: Blends LLM structured outputs with deterministic fallback rule engines, interfacing with Africa's Talking SMS API.
