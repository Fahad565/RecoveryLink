# Product Requirement Document (PRD) - RecoveryLink MVP

## 1. Executive Summary
RecoveryLink is a telecom-accessible digital recovery platform that enables mobile subscribers to prepare for and navigate phone loss via USSD and SMS without relying on active internet access or smart device availability.

## 2. Core Features
- **USSD Interface (`/api/v1/ussd`)**: Supports Africa's Talking form-data menu system (`CON`/`END`).
- **Digital Safety Check**: Interactive assessment of emergency contacts, recovery emails, data backups, and recovery plans.
- **Readiness Scoring**: Algorithm calculating a 0-100 score with personalized advice.
- **Recovery Profile Management**: View and update recovery metadata.
- **Emergency Recovery Mode**: Trigger emergency lost phone procedures, generating an AI-curated recovery plan delivered via SMS.

## 3. Data Privacy & Security
- Passwords, PINs, and OTPs are explicitly prohibited.
- Minimal PII collection focused on contact pointers and readiness status.
