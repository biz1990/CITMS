# CITMS v3.6 - Production Deployment & Operations Guide

This document provides comprehensive instructions for deploying, managing, and maintaining the **Centralized IT Management System (CITMS) v3.6** in a production environment.

---

## 1. System Architecture Overview

CITMS v3.6 follows a micro-services inspired monolithic architecture with a clear separation of concerns:

- **Frontend:** React 18 + Vite + Tailwind CSS + shadcn/ui.
- **Backend:** FastAPI (Python 3.11+) + SQLAlchemy (Async).
- **Database:** PostgreSQL 15+ (with Materialized Views for reporting).
- **Cache & Messaging:** Redis 7+ (for Redis Streams and WebSocket pub/sub).
- **Object Storage:** MinIO (S3 compatible) for asset attachments and reports.
- **Remote Control:** RustDesk (Self-hosted relay and signal server).
- **Task Queue:** Celery + Redis (for background processing and scheduled reports).

---

## 2. Infrastructure Requirements

### Minimum Hardware Specifications
- **CPU:** 4 vCPUs
- **RAM:** 8 GB
- **Storage:** 100 GB SSD (Scalable based on asset volume)
- **Network:** 1 Gbps

### Software Dependencies
- **OS:** Ubuntu 22.04 LTS (Recommended)
- **Docker:** 24.0+
- **Docker Compose:** 2.20+
- **Ansible:** 2.15+ (for automated deployment)

---

## 3. Environment Configuration

Create a `.env` file in the root directory with the following variables:

```env
# --- Core ---
PROJECT_NAME="CITMS v3.6"
ENVIRONMENT=production
SECRET_KEY=your_super_secret_key_change_me
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# --- Database ---
POSTGRES_USER=citms_admin
POSTGRES_PASSWORD=secure_db_password
POSTGRES_DB=citms_prod
DATABASE_URL=postgresql+asyncpg://citms_admin:secure_db_password@db:5432/citms_prod

# --- Redis ---
REDIS_URL=redis://redis:6379/0

# --- MinIO (Object Storage) ---
MINIO_ROOT_USER=minio_admin
MINIO_ROOT_PASSWORD=minio_secure_password
MINIO_ENDPOINT=minio:9000
MINIO_BUCKET=citms-assets

# --- SMTP (Email) ---
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=alerts@yourdomain.com
SMTP_PASSWORD=your_app_password
EMAILS_FROM_EMAIL=alerts@yourdomain.com

# --- RustDesk (Remote Control) ---
RUSTDESK_SERVER=rustdesk.yourdomain.com
RUSTDESK_KEY=your_rustdesk_public_key

# --- Agent Security ---
AGENT_SECRET_KEY=agent_hmac_secret
AGENT_BOOTSTRAP_TOKEN=initial_registration_token
```

---

## 4. Deployment Steps

### 4.0. First-time Setup
If this is your first time deploying CITMS v3.6, please follow the [First-time Setup Guide](FIRST_TIME_SETUP.md) for detailed instructions on initializing the database and creating the first Super Admin.

### 4.1. Automated Deployment (Ansible)

We provide an Ansible playbook for one-click deployment.

1. **Configure Inventory:** Edit `ansible/inventory.ini` with your server IP.
2. **Run Playbook:**
   ```bash
   ansible-playbook -i ansible/inventory.ini ansible/deploy.yml
   ```

### 4.2. Manual Deployment (Docker Compose)

1. **Clone Repository:**
   ```bash
   git clone https://github.com/your-org/citms-v3.6.git
   cd citms-v3.6
   ```
2. **Setup Environment:** Copy `.env.example` to `.env` and fill in values.
3. **Build and Start:**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d --build
   ```
4. **Initialize Database:**
   ```bash
   docker-compose exec backend python -m backend.src.infrastructure.database.init_db
   ```

---

## 5. Database Management

### 5.1. Materialized Views
Reports in CITMS v3.6 rely on Materialized Views for high performance. These views are refreshed automatically via Celery tasks or manually via the Admin UI.

**Manual Refresh Command:**
```sql
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_asset_inventory;
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_ticket_sla_performance;
```

### 5.2. Backup & Restore
**Backup:**
```bash
docker exec -t citms_db pg_dumpall -c -U citms_admin > dump_`date +%d-%m-%Y"_"%H_%M_%S`.sql
```

**Restore:**
```bash
cat dump_file.sql | docker exec -i citms_db psql -U citms_admin
```

---

## 6. Monitoring & Logging

### 6.1. Application Logs
Logs are centralized in the `logs/` directory and can be viewed via:
```bash
docker-compose logs -f backend
```

### 6.2. Health Checks
- **Backend API:** `GET /api/v1/health`
- **Frontend:** `GET /`
- **Redis:** `redis-cli ping`

---

## 7. Security Hardening

1. **SSL/TLS:** Always use Nginx as a reverse proxy with Let's Encrypt SSL certificates.
2. **Firewall:** Only expose ports 80, 443, and 21115-21119 (RustDesk).
3. **Database:** Ensure PostgreSQL is not accessible from the public internet.
4. **2FA:** Enforce Two-Factor Authentication for all Admin accounts in Settings.
5. **Agent Token:** Rotate `AGENT_BOOTSTRAP_TOKEN` after initial deployment.

---

## 8. Troubleshooting

| Issue | Possible Cause | Solution |
| :--- | :--- | :--- |
| **WebSocket Disconnected** | Redis down or Proxy config | Check Redis logs; Ensure Nginx supports `Upgrade` header. |
| **Reports are Empty** | MV not refreshed | Run `REFRESH MATERIALIZED VIEW` manually. |
| **Agent Registration Failed** | Invalid Bootstrap Token | Verify `X-Bootstrap-Token` in Agent config matches `.env`. |
| **Remote Control Failed** | RustDesk relay down | Check RustDesk container status and firewall ports. |

---

## 9. CI/CD Pipeline

CITMS v3.6 includes a GitHub Actions workflow (`.github/workflows/deploy.yml`) that:
1. Runs Unit & Integration Tests.
2. Builds Docker Images.
3. Pushes to Private Registry.
4. Triggers Ansible deployment on the production server.

---

**Document Version:** 1.0  
**Last Updated:** April 7, 2026  
**Author:** CITMS Architecture Team
