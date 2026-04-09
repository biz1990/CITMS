# CITMS v3.6 Production Deployment Guide

This document provides the final technical instructions for deploying the Centralized IT Management System (CITMS) v3.6 in both Local (Development/Staging) and Production environments.

## 1. Prerequisites
- **OS**: Ubuntu 22.04 LTS (Recommended)
- **Database**: PostgreSQL 15+ with `pg_cron` extension
- **Cache/Event Bus**: Redis 7.0+
- **Runtimes**: Python 3.10+, Node.js 20+
- **Remote Control**: RustDesk Server (Pro or Self-hosted)

---

## 2. Backend Setup (Production)

### 2.1. Environment Variables
Create a `.env` file in the `backend` directory:
```bash
POSTGRES_USER=citms_admin
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=citms_v3
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=generate_a_secure_random_string
RUSTDESK_API_URL=https://rustdesk.yourdomain.com
RUSTDESK_API_TOKEN=your_rustdesk_token
```

### 2.2. Database Optimization
Before running migrations, Ensure `pg_cron` is listed in `shared_preload_libraries` in `postgresql.conf`:
```bash
# Edit /etc/postgresql/15/main/postgresql.conf
shared_preload_libraries = 'pg_cron'
cron.database_name = 'citms_v3'
```
Restart PostgreSQL: `sudo systemctl restart postgresql`

### 2.3. Run Migrations
```bash
cd backend
python3 -m pip install -r requirements.txt
python3 -m alembic upgrade head
```

### 2.4. Performance Verification
Ensure GIN indexes are active:
```sql
SELECT * FROM pg_indexes WHERE indexname = 'ix_audit_logs_details_gin';
```

---

## 3. Frontend Setup (Production)

### 3.1. Build PWA
```bash
cd frontend
npm install
npm run build
```

### 3.2. Web Server (Nginx)
Sample Nginx configuration for CITMS:
```nginx
server {
    listen 80;
    server_name citms.yourdomain.com;

    location / {
        root /var/www/citms/dist;
        try_files $uri $uri/ /index.html;
    }

    location /api/v1 {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
    }
}
```

---

## 4. Maintenance & Operations

### 4.1. Automated View Refreshes
The system uses `pg_cron` to refresh inventory materialized views every 15 minutes. Monitor with:
```sql
SELECT * FROM cron.job_run_details ORDER BY start_time DESC LIMIT 10;
```

### 4.2. Backup Strategy
- **Daily DB Dump**: `pg_dump -Fc citms_v3 > /backups/citms_$(date +%F).dump`
- **Retention**: Keep 30 days of backups.

---

## 5. Security Checklist
- [ ] Change all default passwords.
- [ ] Enable HTTPS via certbot.
- [ ] Configure Firewall (Allow 80, 443, and 21115-21119 for RustDesk).
- [ ] Verify Row-Level Security (RLS) policies are active.

---
**Prepared by:** Antigravity Solution Architect
**Status:** READY FOR PRODUCTION
