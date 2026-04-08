# CITMS v3.6 - First-time Deployment & Initial Setup Guide

This guide provides step-by-step instructions for deploying CITMS v3.6 for the first time and setting up the initial Super Admin account.

## Prerequisites

- Docker and Docker Compose installed.
- SMTP Server credentials (for notifications).
- RustDesk Server (optional, for remote control).
- MinIO or S3-compatible storage (for asset attachments).

---

## Step 1: Environment Configuration

1. Clone the repository and navigate to the project root.
2. Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

3. Update the following critical variables in `.env`:
   - `POSTGRES_PASSWORD`: Strong password for the database.
   - `SECRET_KEY`: Random string for JWT signing.
   - `AGENT_SECRET_KEY`: Random string for agent authentication.
   - `REDIS_PASSWORD`: Password for Redis.
   - `SMTP_*`: Email server configurations.

---

## Step 2: Launch Infrastructure

Start the core services (PostgreSQL, Redis, MinIO) using Docker Compose:

```bash
docker-compose up -d db redis minio
```

Wait for the database to be ready.

---

## Step 3: Run Database Migrations

Apply the database schema using Alembic:

```bash
docker-compose run --rm backend alembic upgrade head
```

---

## Step 4: System Initialization

Initialize the system with default roles and permissions. This step is required before creating the first user.

```bash
docker-compose run --rm backend python backend/src/scripts/init_system.py init
```

This command will:
- Create default permissions for all modules.
- Create default roles: `SUPER_ADMIN`, `IT_MANAGER`, `IT_STAFF`, `DEPARTMENT_HEAD`, `REGULAR_USER`.
- Assign all permissions to the `SUPER_ADMIN` role.

---

## Step 5: Create the First Super Admin

You can create the first Super Admin using the CLI script. This mechanism is automatically disabled once the first user is created.

```bash
docker-compose run --rm backend python backend/src/scripts/init_system.py create-superuser <username> <email> <full_name> <password>
```

**Example:**
```bash
docker-compose run --rm backend python backend/src/scripts/init_system.py create-superuser admin admin@citms.local "System Administrator" "P@ssw0rd123456"
```

*Note: The password must be at least 12 characters long and contain uppercase, lowercase, and digits.*

---

## Step 6: Start Application Services

Now start the Backend and Frontend services:

```bash
docker-compose up -d backend frontend
```

The system should now be accessible at:
- Frontend: `http://localhost:3000`
- API Docs: `http://localhost:8000/docs`

---

## Step 7: Post-Setup Configuration

1. **Login:** Access the dashboard and log in with your new Super Admin credentials.
2. **System Settings:** Navigate to `Settings` to configure:
   - SMTP Server details for email alerts.
   - RustDesk API/ID Server for Remote Control.
   - MinIO Buckets for asset storage.
3. **Notification Preferences:** Configure default alert types and holiday schedules.
4. **Inventory Agent:** Download and deploy the CITMS Agent to target devices using the `AGENT_SECRET_KEY`.

---

## Troubleshooting

- **Database Connection Issues:** Ensure `POSTGRES_HOST` matches the service name in `docker-compose.yml`.
- **Permission Denied:** If you cannot access certain modules, verify your role in the `User Management` section.
- **Migration Errors:** If migrations fail, ensure the database is empty or at the correct version.

---

## Security Recommendations

- **Disable Superuser Endpoint:** The `/auth/init-superuser` endpoint is automatically protected, but for maximum security, ensure it is not exposed to the public internet during setup.
- **Rotate Keys:** Periodically rotate `SECRET_KEY` and `AGENT_SECRET_KEY`.
- **SSL/TLS:** Always deploy behind a reverse proxy (Nginx/Traefik) with valid SSL certificates in production.
