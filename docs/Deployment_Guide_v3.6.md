# Hướng dẫn Triển khai Hệ thống CITMS v3.6 (Deployment Guide)

Tài liệu này cung cấp hướng dẫn toàn diện từng bước để triển khai Hệ thống Quản trị CNTT Tập trung (CITMS - Centralized IT Management System) phiên bản 3.6 từ môi trường Development, Staging đến Production.

---

## 1. Tổng quan Triển khai

### 1.1. Kiến trúc hệ thống
Hệ thống CITMS 3.6 tuân theo kiến trúc Modular Monolith Domain-Driven Design (DDD):
- **Frontend App:** Truy cập qua React PWA (Vite + TailwindCSS + React Flow), cung cấp cache offline và đồng bộ dữ liệu.
- **Backend API:** FastAPI (Async) xử lý core logic, bảo mật và kết nối DB.
- **Background Workers:** Celery kết nối với Redis để chạy background tasks, cron jobs, event-driven processing.
- **Database Layer:** PostgreSQL 16 tích hợp Soft Delete, Triggers, Row-Level Security, Materialized Views, và pg_cron.
- **Cache & Message Broker:** Redis 7 xử lý Cache, Notification Stream và Celery Broker.
- **Storage Layer:** MinIO đóng vai trò S3-compatible lưu trữ hình ảnh, backup, chứng từ.
- **Reverse Proxy:** Nginx kết hợp SSL (Let's Encrypt), Rate Limiting.

### 1.2. Yêu cầu Cấu hình Tối thiểu
**Môi trường Local / Staging:**
- CPU: 4 Cores
- RAM: 8 GB
- Storage: 50 GB SSD

**Môi trường Production (Dự kiến 10,000+ thiết bị):**
- CPU: 8 Cores (hoặc 2x VM 4 cores)
- RAM: 16 GB - 32 GB
- Storage: 200 GB+ NVMe SSD
- OS: Ubuntu 22.04 LTS hoặc Ubuntu 24.04 LTS

---

## 2. Chuẩn bị Hệ thống (Host OS)

Cài đặt các dependency cần thiết trên server Linux.

### 2.1. Cài đặt Docker & Docker Compose
```bash
# Gỡ bản cũ
sudo apt-get remove docker docker-engine docker.io containerd runc

# Cài đặt prerequisites
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg lsb-release

# Thêm GPG key của Docker
sudo mkdir -m 0755 -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Thêm repo
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Cài đặt docker
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Phân quyền cho User (khỏi dùng sudo)
sudo usermod -aG docker $USER
newgrp docker
```

### 2.2. Chuẩn bị Domain & Cấu hình SSL
```bash
# Cài đặt Nginx & Certbot
sudo apt-get install -y nginx certbot python3-certbot-nginx

# Mở port Firewall (UFW)
sudo ufw allow 'Nginx Full'
sudo ufw allow 22/tcp

# Sinh chứng chỉ SSL cho Domain chính
sudo certbot --nginx -d citms.yourdomain.com
```

---

## 3. Cấu hình Biến Môi trường (`.env`)

Tạo file `.env` từ `.env.example` tại thư mục root của dự án. 

```bash
cp .env.example .env
nano .env
```

*Cấu hình các tham số quan trọng:*
```ini
# CORE
ENVIRONMENT=production
PROJECT_NAME="CITMS v3.6"
DOMAIN=citms.yourdomain.com
API_V1_STR=/api/v1
SECRET_KEY="<GENERATE_RANDOM_SECURE_STRING_HERE_MIN_32_CHARS>"

# DATABASE (Postgres 16)
POSTGRES_SERVER=db
POSTGRES_PORT=5432
POSTGRES_DB=citms_db
POSTGRES_USER=citms_admin
POSTGRES_PASSWORD=<STRONG_DB_PASS>

# THÔNG TIN KẾT NỐI DB CHO BACKEND (SQLAlchemy Base)
SQLALCHEMY_DATABASE_URI=postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_SERVER}:${POSTGRES_PORT}/${POSTGRES_DB}
SYNC_DATABASE_URI=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_SERVER}:${POSTGRES_PORT}/${POSTGRES_DB}

# REDIS (Message Broker & Cache)
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=<REDIS_PASS_OPTIONAL>
CELERY_BROKER_URL=redis://:${REDIS_PASSWORD}@${REDIS_HOST}:${REDIS_PORT}/0
CELERY_RESULT_BACKEND=redis://:${REDIS_PASSWORD}@${REDIS_HOST}:${REDIS_PORT}/0

# MINIO (S3 Compatible)
MINIO_ROOT_USER=minio_admin
MINIO_ROOT_PASSWORD=<MINIO_PASS>
S3_ENDPOINT=http://minio:9000
S3_ACCESS_KEY=${MINIO_ROOT_USER}
S3_SECRET_KEY=${MINIO_ROOT_PASSWORD}
S3_BUCKET_NAME=citms-attachments
S3_REGION=ap-southeast-1

# SMTP
SMTP_TLS=True
SMTP_PORT=587
SMTP_HOST=smtp.gmail.com
SMTP_USER=no-reply@yourdomain.com
SMTP_PASSWORD=<APP_PASSWORD>

# RUSTDESK (Optional - nếu tự host)
RUSTDESK_ID_SERVER=rustdesk.yourdomain.com
RUSTDESK_RELAY_SERVER=rustdesk.yourdomain.com
```

---

## 4. Triển khai bằng Docker Compose (Local / Staging / Prod-Single)

Cấu trúc file `docker-compose.yml` định nghĩa đầy đủ 5 services: `db`, `redis`, `minio`, `api`, `celery_worker`.

**Thứ tự khởi động (Rất quan trọng):**
Phải khởi tạo Storage và Database trước khi khởi động API.

```bash
# 1. Khởi động DB, Redis, MinIO
docker compose up -d db redis minio

# Chờ 30 giây cho PostgreSQL khởi động hẳn trong lần đầu khởi tạo
sleep 30

# 2. Khởi động API Backend (chạy migration lúc khởi động)
docker compose up -d api

# 3. Khởi động Background Workers
docker compose up -d worker event_worker
```

---

## 5. Database Setup (PostgreSQL)

Hệ thống CITMS yêu cầu các Extension đặc biệt.

### 5.1. Bật Extension (Chạy bên trong Docker DB Container)
```bash
docker exec -it <db_container_name> psql -U citms_admin -d citms_db
```
Bên trong Console psql:
```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_cron";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
```

### 5.2. Chạy Migration Alembic
Trong CITMS, cấu hình Uvicorn script ở service `api` đã tự động chạy `alembic upgrade head`, tuy nhiên để chạy thủ công:
```bash
docker exec -it <api_container_name> alembic upgrade head
```

### 5.3. Khởi tạo Seed Data (Quyền, Roles hạn mức)
Khởi tạo dữ liệu bắt buộc (Row-Level Security, Asset Statuses, Master Table):
```bash
docker exec -it <api_container_name> python backend/scripts/seed_initial_data.py
```

---

## 6. Redis Configuration

Redis đóng vai trò là Broker cho Celery và Event Stream.

Tạo Consumer Group cho Event Notifications:
```bash
docker exec -it <redis_container_name> redis-cli
> XGROUP CREATE citms:events:notification notification_consumers $ MKSTREAM
> XGROUP CREATE citms:events:audit audit_consumers $ MKSTREAM
```
*(Lưu ý: API Core có thể đã tự khởi tạo qua module `redis_manager.py`, có thể kiểm tra qua log backend)*

---

## 7. MinIO (S3-Compatible) Configuration

1. Truy cập giao diện MinIO tại: `http://<server-ip>:9001`
2. Đăng nhập với `MINIO_ROOT_USER` & `MINIO_ROOT_PASSWORD`
3. Quản lý Buckets:
   - Tạo Bucket `citms-attachments`
   - Chuyển Access Policy sang `Public` (để Frontend hiển thị hình ảnh tự động) hoặc `Custom` có kèm quy tắc GET object.
4. (Optional) Tạo Access Key riêng cho Frontend và Backend.

---

## 8. Backend & Celery Workers

**Build image Backend (nếu build từ mã nguồn):**
```bash
docker compose build api worker
```

**Khởi động Uvicorn (FastAPI):**
```bash
docker compose up -d api
```

**Khởi động hai luồng Celery:**
- `worker`: Xử lý import excels, scan network, gen báo cáo.
- `event_worker`: Lắng nghe Redis Streams đẩy realtime tới WebSocket/Email.
```bash
docker compose up -d worker
docker compose up -d event_worker
```
*(Các service này được định cấu hình bằng profile hoặc entrypoint riêng trong `docker-compose.yml`)*

---

## 9. Frontend (React PWA)

Triển khai build cho Frontend. Không sử dụng development server `vite dev`.

### 9.1. Build Production
```bash
# Cài Node.js > 20
npm install
# Xây dựng biến môi trường VITE
cp .env.example .env
nano .env  # set VITE_API_URL=https://citms.yourdomain.com/api/v1
# Build
npm run build
```
Kết quả thư mục `dist` chứa file Frontend tối ưu nhất.

### 9.2. Phân phối qua Nginx Host
```bash
# Trỏ nginx tới thư mục build frontend. (Nếu triển khai docker-compose có thể include frontend trực tiếp bằng nginx-alpine image)
sudo rm -rf /var/www/citms-frontend
sudo mv dist/ /var/www/citms-frontend
sudo chown -R www-data:www-data /var/www/citms-frontend
```

---

## 10. Production Deployment (Nginx Reverse Proxy & Security)

Cấu hình cho Nginx (giả định file là `/etc/nginx/sites-available/citms`)

```nginx
server {
    listen 80;
    server_name citms.yourdomain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name citms.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/citms.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/citms.yourdomain.com/privkey.pem;

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-XSS-Protection "1; mode=block";
    add_header X-Content-Type-Options "nosniff";

    # Gzip
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # Frontend SPA Rules
    location / {
        root /var/www/citms-frontend;
        index index.html index.htm;
        try_files $uri $uri/ /index.html;
    }

    # API Proxy Rules
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket Notifications
    location /api/v1/ws/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400s;
        proxy_send_timeout 86400s;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/citms /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

*(Ghi chú: Trong thư mục mã nguồn có cung cấp sẵn Playbook Ansible, nếu bạn có cụm Backend/Frontend riêng biệt, hãy chạy: `ansible-playbook -i hosts.ini ansible/site.yml`)*

---

## 11. Post-Deployment Steps

Sau khi deploy xong, hãy thực hiện kiểm tra.

### 11.1. Tạo Super Admin (Lần đầu truy cập)
```bash
docker exec -it <api_container_name> python backend/scripts/create_super_admin.py --email admin@domain.com --password "Admin@123!!"
```

### 11.2. Xác nhận Frontend Offline-First
- Mở F12 -> Application -> Service Workers (Phải ở trạng thái *Activated & Running*)
- Mở tab Cache Storage, xem `citms-static-cache` và `citms-api-cache` có hoạt động.

### 11.3. Xác nhận Real-time Stream
- Đăng nhập, mở màn hình Dashboard.
- Cập nhật một thiết bị bằng Postman / Tab khác.
- Kiểm tra xem Notification UI trên trang web có nhảy lên ngay lập tức mà không cần F5 (Websocket + Redis Stream).

---

## 12. Monitoring & Observability

Để đảm bảo Service Level Agreement (SLA) tại Production:

1. **Prometheus & Grafana**:
   Backend đã trang bị library `prometheus-fastapi-instrumentator`. Kéo metric tại endpoint `/api/metrics` trên Nginx nếu từ dải IP nội bộ.
2. **PostgreSQL pg_stat_statements**:
   Cho phép theo dõi slow query qua hệ thống DB Monitoring.
3. **Sentry Error Tracking**:
   Nếu cần gom nhóm lỗi Backend, cung cấp biến `SENTRY_DSN` trong `.env`.

---

## 13. Backup & Restore Strategy

**1. Backup Database tự động (Cron job trên server Host)**
Tạo bash script `/opt/scripts/backup_db.sh`:
```bash
#!/bin/bash
DATE=$(date +%Y-%m-%d_%H-%M-%S)
docker exec <db_container_name> pg_dump -U citms_admin citms_db | gzip > /backups/db/citms_db_$DATE.sql.gz
```
Chèn vào `crontab -e`: `0 2 * * * /opt/scripts/backup_db.sh`

**2. Backup MinIO**
Sử dụng công cụ `mc` (MinIO Client):
```bash
mc alias set local http://localhost:9000 minio_admin MINIO_PASS
mc mirror local/citms-attachments /backups/minio/citms-attachments
```

**3. Khôi phục (Restore)**
```bash
gunzip -c citms_db_YYYY-MM-DD.sql.gz | docker exec -i <db_container_name> psql -U citms_admin -d citms_db
```

---

## 14. Troubleshooting Guide

**Lỗi 1: `502 Bad Gateway` trên Nginx**
- Nguyên nhân: FastAPI Backend (API) chưa sẵn sàng hoặc bị chết.
- Xử lý: `docker compose logs -f api`. Khởi động lại container: `docker compose restart api`.

**Lỗi 2: Lỗi Cors (`Has been blocked by CORS policy`) trên Frontend**
- Nguyên nhân: Thiếu cấu hình BACKEND_CORS_ORIGINS trong `.env`.
- Xử lý: Cập nhật `.env` cho backend để chấp nhận Domain Nginx. Ví dụ: `BACKEND_CORS_ORIGINS=["https://citms.yourdomain.com", "http://localhost:5173"]`

**Lỗi 3: Lỗi thiếu Redis Group khi WebSocket Listener chạy**
- Xử lý: `docker exec -it <api_container_name> python backend/scripts/init_redis_streams.py`

**Lỗi 4: Lỗi Database Migration `Table already exists`**
- Sử dụng Alembic stamp cho phiên bản hiện tại, hoặc drop DB đi để Re-run Migration nếu đây là DB mới hoàn toàn (do chạy seed lại).

---

## 15. Checklist Trước Khi Go-Live

- [x] HTTPS/SSL (Let's Encrypt) gia hạn tự động qua Certbot Timer.
- [x] Biến `.env` SECRET_KEY đã được thay thế (không sử dụng giá trị mặc định).
- [x] Database chạy trên Volume Persistent (`postgres_data`).
- [x] MinIO chạy trên Volume Persistent (`minio_data`).
- [x] Service Worker PWA đã cài và kiểm tra bypass qua HTTPS Nginx.
- [x] Đã cấu hình UFW (tường lửa) chỉ mở Port `80, 443, 22`. Chặn cổng DB `5432` hoặc MinIO `9000` ra ngoài Internet nếu không cần thiết.
- [x] SMTP Setup đã gửi mail qua `Sendgrid/SES/Gmail` thành công.
- [x] Hệ thống Backup script đã chạy thử ít nhất 1 lần khôi phục.

**(Hết tài liệu Hướng dẫn Triển khai)**
