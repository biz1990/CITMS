# CITMS 3.6 Operations Manual & Deployment Runbook

This document provides instructions for deploying, operating, and managing the CITMS 3.6 application.

## 1. Deployment Runbook

### Prerequisites
- Ansible 2.12+
- Docker and Docker Compose on target servers
- SSH access to target servers
- Configured `.env` file (see `.env.example`)

### Deployment Steps
1. **Prepare Inventory:** Update the `ansible/inventory` file with your target server IP addresses.
2. **Configure Variables:** Update `ansible/vars/main.yml` with environment-specific settings (e.g., database credentials, RustDesk URL).
3. **Run Playbook:** Execute the main deployment playbook:
   ```bash
   ansible-playbook -i ansible/inventory ansible/deploy.yml
   ```
4. **Verify Deployment:**
   - Check if containers are running: `docker ps`
   - Access the application via the configured domain (e.g., `https://citms.example.com`).
   - Run health checks: `curl https://citms.example.com/api/health`

---

## 2. Operations Manual

### Service Management
The CITMS 3.6 application runs as a set of Docker containers. Use `docker-compose` to manage them:
- **Start Services:** `docker-compose up -d`
- **Stop Services:** `docker-compose down`
- **Restart Services:** `docker-compose restart`
- **View Logs:** `docker-compose logs -f [service_name]` (e.g., `api`, `spa`, `db`)

### User Management
- **LDAP Sync:** Users are automatically synchronized from LDAP/Active Directory.
- **Admin Access:** The first user synchronized from LDAP with the `IT_ADMIN` group will be granted administrative privileges.
- **Manual Role Assignment:** Admins can assign roles to users via the "Settings > User Management" section in the application.

### Asset Management
- **Import Assets:** Use the "Assets > Import" feature to bulk-upload asset data from CSV files.
- **Remote Access:** Click the "Remote Control" button on an asset's detail page to initiate a Zero-Password RustDesk session.

### Physical Inventory
- **Offline Mode:** Ensure the PWA is installed on the staff's mobile device.
- **Syncing:** Staff must click the "Sync" button in the PWA once they are back online to upload their inventory scans.

---

## 3. Troubleshooting

### Common Issues
- **Database Connection Failure:** Check if the `db` container is running and the `POSTGRES_PASSWORD` in `.env` matches the database configuration.
- **Redis Connection Failure:** Check if the `redis` container is running. This will affect pessimistic locking and session management.
- **RustDesk Integration Error:** Verify the `RUSTDESK_API_URL` and `RUSTDESK_TOKEN` are correct in the environment variables.
- **PWA Sync Failure:** Check the browser's console for IndexedDB errors or network timeout messages.

### Log Locations
- **API Server:** `docker-compose logs api`
- **PostgreSQL:** `docker-compose logs db`
- **Nginx (Proxy):** `docker-compose logs nginx`
- **Sentry:** Access the Sentry dashboard for detailed application error logs.
