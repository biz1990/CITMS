# CITMS 3.6 Maintenance, Backup, Restore, and Monitoring

This document provides guidelines for maintaining the CITMS 3.6 application, including backup/restore procedures and monitoring setup.

## 1. Maintenance Guide

### Regular Maintenance Tasks
- **Software Updates:** Regularly update the CITMS 3.6 application and its dependencies (Node.js, PostgreSQL, Redis, Docker).
- **Security Patches:** Apply security patches to the host operating system and Docker containers.
- **Database Vacuuming:** Periodically run `VACUUM ANALYZE` on the PostgreSQL database to optimize performance.
- **Log Rotation:** Ensure Docker and Nginx logs are rotated to prevent disk space issues.

### System Health Checks
- **API Health:** `GET /api/health`
- **Database Health:** `SELECT 1;`
- **Redis Health:** `PING`
- **RustDesk Health:** `GET /api/rustdesk/status`

---

## 2. Backup and Restore

### Database Backup
CITMS 3.6 uses PostgreSQL. Use `pg_dump` for regular backups:
- **Manual Backup:**
  ```bash
  docker exec -t [db_container_id] pg_dump -U [db_user] [db_name] > backup_$(date +%Y%m%d).sql
  ```
- **Automated Backup:** Set up a cron job to run the backup script daily and store the SQL files in a secure off-site location (e.g., S3, Google Cloud Storage).

### Database Restore
To restore the database from a backup:
1. **Stop Services:** `docker-compose stop api`
2. **Restore Data:**
   ```bash
   cat backup_file.sql | docker exec -i [db_container_id] psql -U [db_user] [db_name]
   ```
3. **Restart Services:** `docker-compose start api`

### Configuration Backup
Regularly back up the `.env` file and the `ansible/` directory, as they contain critical environment-specific settings and deployment playbooks.

---

## 3. Monitoring (Sentry + Prometheus + Grafana)

### Sentry (Error Tracking)
- **Setup:** Configure the `SENTRY_DSN` in the `.env` file for both the API and the SPA.
- **Usage:** Access the Sentry dashboard to view real-time error reports, stack traces, and performance profiles.
- **Alerting:** Set up Sentry alerts to notify the IT team via email or Slack when new errors occur.

### Prometheus (Metrics Collection)
- **Setup:** Prometheus is configured to scrape metrics from the `/api/metrics` endpoint of the API server.
- **Metrics:**
  - **Node.js:** CPU usage, memory usage, event loop lag, GC metrics.
  - **PostgreSQL:** Active connections, query latency, transaction throughput.
  - **Redis:** Memory usage, cache hit rate, active locks.
- **Configuration:** Update `prometheus/prometheus.yml` with the target API server IP.

### Grafana (Visualization)
- **Setup:** Grafana is configured to use Prometheus as a data source.
- **Dashboards:**
  - **CITMS Overview:** High-level system health and performance.
  - **Database Performance:** Detailed PostgreSQL metrics.
  - **API Server Health:** Node.js and Express metrics.
- **Alerting:** Set up Grafana alerts to trigger notifications when metrics exceed predefined thresholds (e.g., high CPU usage, low database connections).

### Infrastructure Monitoring
- **Host Metrics:** Monitor the host server's CPU, memory, disk, and network usage using Prometheus Node Exporter.
- **Container Health:** Monitor the status and resource usage of all Docker containers using cAdvisor.
