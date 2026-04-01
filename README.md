# CITMS - Centralized IT Management System (v3.0)

![System Status](https://img.shields.io/badge/status-production_ready-green)
![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)
![License](https://img.shields.io/badge/license-Enterprise-blue)

CITMS is an Enterprise-Grade infrastructure tracking system built globally with a modular monolith architecture. Featuring Zebra device auto-reconciliation, ITSM ticket workflows, software licensing tracking, and real-time SLA evaluations utilizing Redis and Celery.

## Technology Stack
* **Backend:** FastAPI, PostgreSQL 16 (Partitioning/Triggers), SQLAlchemy 2, Celery
* **Frontend:** React 18, Vite, TypeScript, Ant Design Pro 5.x, React Flow, Zustand, PWA.
* **DevOps:** Docker Swarm / Compose, Nginx, GitHub Actions

## Installation & Deployment Guide

### 1. Development Mode (Hot-Reloading)

**Prerequisites:** Node.js v18+, Python 3.11+, and Docker.

```bash
# 1. Spin up the underlying DB services
docker-compose up -d db redis minio

# 2. Run Backend Migrations & Seeding
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python scripts/seed.py
uvicorn app.main:app --reload

# 3. Start the Frontend
cd frontend
npm install
npm run dev
```

### 2. Staging / Testing Mode (QA)

Run the full testing harness covering Business Rules, Role-based constraints, and Exception Handling.

```bash
cd backend
python -m pytest tests/ --cov=app --cov-report=term-missing
```

### 3. Production Deployment (Dockerized)

Ensure you create securely configured `.env.prod` environment variable file replacing placeholders.

```bash
# Bring the entire environment up.
docker-compose -f docker-compose.prod.yml up -d --build

# Scale Celery asynchronous workers specifically if load increases
docker-compose -f docker-compose.prod.yml up -d --scale celery_worker=3
```
* **Frontend Client:** Available directly at `http://your-server-ip/`
* **API endpoints:** Routed seamlessly through `http://your-server-ip/api/v1`

## Background Tiers & Cronjobs
Handled elegantly by **Celery Beat**:
- **04:00 AM (Daily):** Deep LDAP AD syncs to validate onboarding structures.
- **`*/5` Mins:** SLA Sweeps. Pings managers via Mail/WebSockets if tickets breach limits.

_For further domain mapping, read `docs/CITMS_doc.md` constraints matrices._
