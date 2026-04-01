# HƯỚNG DẪN TRIỂN KHAI CITMS TRÊN UBUNTU 22.04 LTS
**Phiên bản Hệ thống:** CITMS v3.0 (Staging / Thử nghiệm)
**Soạn thảo bởi:** Senior DevOps Engineer

---

## 1. Mở Đầu & Kiến Trúc
Tài liệu cung cấp chu trình nguyên gốc (step-by-step) vô cùng nghiêm ngặt để khởi dựng toàn bộ dự án **Centralized IT Management System (CITMS)** sử dụng nền tảng Container hoá.

### 1.1 Mục Đích
Triển khai hệ thống lên máy chủ thử nghiệm (Staging) để UAT (User Acceptance Testing) và kiểm định tích hợp phần cứng Zebra/GLPI theo tài liệu SRS v3.0.

### 1.2 Yêu Cầu Cấu Hình Máy Chủ (Minimum Specs)
* **OS**: Ubuntu 22.04 LTS (Kiểm định tính tương thích tốt nhất)
* **CPU**: 4 vCores (Xử lý đa luồng Backend Gunicorn + Worker Celery Pydantic)
* **RAM**: 8 GiB (Ngăn chặn OOM Killer cho PostgreSQL/Redis)
* **Disk/Storage**: Từ 50GB NVMe hoặc SSD (Ưu tiên Database IOPS)
* **Network**: IP Tĩnh (Static IP) mạng LAN/WAN.

### 1.3 Công Nghệ Triển Khai Thực Tế
* Node Orchestration: `Docker` & `Docker Compose v2`
* Data Layer: `PostgreSQL 16` (Partitioning Time-Series), `Redis 7` (Pub/Sub & Broker)
* Object Storage: `MinIO` (S3-compatible API lưu đính kèm Ticket)
* Core API: `FastAPI` + `Celery Beat/Worker`
* Interface: `Nginx:Alpine` serve SPA `React 18` + `Vite`

---

## 2. Tiền Cài Đặt (Prerequisites)

> [!IMPORTANT]
> Trước khi thực thi bất kỳ lệnh nào, bạn CẦN sử dụng một tài khoản non-root có quyền `sudo`. Không chạy trực tiếp trên `root` để tránh leo thang đặc quyền.

### Cập Nhật Apt & Package Cơ Bản
```bash
sudo apt-get update -y && sudo apt-get upgrade -y
sudo apt-get install -y ca-certificates curl gnupg lsb-release git unzip ufw
```

### Kiến Trúc Mạng & Bảng Firewall (UFW)
Hệ thống mạng (Bridge Network) của Docker ẩn dấu các port Backend/DB bên trong máy chủ. Tuy nhiên, ta CẦN mở các Port Ingress sau:

| Dịch Vụ | Port | Giao thức | Ý Nghĩa (Public/Private) |
|---|---|---|---|
| SSH | `22` | TCP | Remote System Admin |
| Nginx (Web) | `80` | TCP | Truy cập Web Front-End |
| MinIO S3 API | `9000` | TCP | Upload đính kèm ITSM |
| MinIO Console | `9001` | TCP | Quản trị Object Storage |
| Backend Core | `8000` | TCP | Giao tiếp Inventory Ingestion trực tiếp từ Agent |

**Bật Firewall chặn các cổng rác:**
```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 9000/tcp
sudo ufw allow 9001/tcp
# Mở 8000 cho GLPI Agent gửi báo cáo thẳng vào core API (tùy chọn staging)
sudo ufw allow 8000/tcp
sudo ufw --force enable
```

---

## 3. Quá Trình Cài Đặt (Step-by-step Installation)

### Bước 1: Cài Đặt Docker & Docker Compose Engine
Thêm khóa GPG và nạp Repository Docker chính thức về cho Ubuntu:
```bash
sudo mkdir -m 0755 -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update -y
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Cấp quyền cho user chạy Docker không cần sudo
sudo usermod -aG docker ${USER}
# (Bạn cần log out sau đó log in lại để thay đổi có hiệu lực)
```

### Bước 2: Kéo Mã Nguồn (Clone Repository)
```bash
cd /opt
sudo mkdir citms && sudo chown ${USER}:${USER} citms
git clone https://github.com/your-org/CITMS.git /opt/citms
cd /opt/citms
```

### Bước 3: Build Tham Số Môi Trường (`.env`)
Sao chép cấu hình mẫu và thay đổi các mật khẩu (Rất quan trọng):
```bash
cp .env.example .env.prod
nano .env.prod
```
Nội dung khai báo mẫu `.env.prod`:
```ini
POSTGRES_USER=citms_admin
POSTGRES_PASSWORD=YourStrongDBPassword123!
POSTGRES_DB=citms_prod
REDIS_URL=redis://redis:6379/0
SECRET_KEY=TaoMotChuoiBase64NgauNhienDai32KyTu
API_V1_STR=/api/v1
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioSecretKey!
```

### Bước 4: Khởi Động Đội Hình `Docker Compose`
Quy trình nạp tự động Nginx $\rightarrow$ FastAPI $\rightarrow$ Postgres $\rightarrow$ Redis $\rightarrow$ Celery Beat/Worker:
```bash
docker compose -f docker-compose.prod.yml up -d --build
```
> [!TIP]
> Tham số `--build` ép Docker rebuild ảnh Nginx Frontend (Chạy Multi-stage xuất file tĩnh ra `/dist` nạp vào Alpine) và Gunicorn Backend bằng file Dockerfile tích hợp.

### Bước 5: Cấy Lược Đồ Dữ Liệu (Alembic Migration)
Đâm xuyên vào Container hệ thống Backend đang chạy và nạp Schema (Bảng/Partition Time Series/Triggers) vào Postgres v16:
```bash
docker compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

### Bước 6: Đổ Data Mẫu Hệ Thống (Base Seeding)
Tự động nạp Role Matrix, System Cfg mặc định bằng Python Script:
```bash
docker compose -f docker-compose.prod.yml exec backend python scripts/seed.py
```

### Bước 7: Kiểm Tra Endpoint Sẵn Sàng
```bash
# Kiểm thử Frontend
curl -I http://localhost:80/

# Kiểm thử Backend Swagger UI / RFC Health Check
curl -I http://localhost:8000/docs
```

---

## 4. Cấu Hình Vận Hành & Khớp Nối Hạ Tầng (Post-Installation)

### 1. Khai báo Super Admin Mật Khẩu Khởi Trị
Lệnh này chọc thẳng vào Service Backend thông qua CLI quản trị, tận dụng Base Repository để gen User:
```bash
docker compose -f docker-compose.prod.yml exec backend python -c "
import asyncio
from app.api.deps import AsyncSessionLocal
from app.services.auth import AuthService
async def cr():
    async with AsyncSessionLocal() as db:
        await AuthService(db).create_super_admin('superadmin', 'TempPass@2026', 'admin@corp.com')
asyncio.run(cr())
"
```

### 2. Connect Cổng Inventory GLPI / Agent
Tại trạm theo dõi thiết bị (PC User/Máy quét Zebra ngầm), bạn cấu hình Endpoint để Agent ping định kỳ:
**Endpoint Tracking Target**: `http://<IP_MAY_CHU_UBUNTU>:8000/api/v1/inventory/ingest`
Backend sẽ dùng Middleware xử lý `asset_tag` / `primary_mac` / `serial_number` đổ vào DB (Tự Reconcile Docking trạm sạc Zebra).

### 3. Backup System Tự Động Định Kỳ (Cron)
Tạo Cronjob Server OS lấy Dump SQL siêu an toàn để lưu trữ riêng:
```bash
crontab -e
# Thêm dòng dưới vào trình soạn thảo (chạy 2 giờ sáng mỗi ngày)
0 2 * * * docker exec citms-db-1 pg_dump -U citms_admin citms_prod | gzip > /opt/citms/backups/db_$(date +\%Y\%m\%d).sql.gz
```

---

## 5. Nghiệm Thu Hệ Thống (Verification)

Sau khi hoàn tất, rà soát 4 Checkpoints sau:

**1. Sức khỏe Containers (Up Status):**
```bash
docker compose -f docker-compose.prod.yml ps
# Trạng thái mong muốn: Trạng thái 'Up' cho toàn bộ 6/6 container. Không xuất hiện log 'Restarting'.
```

**2. Quản Lý PWA Giao Diện (UI):**
- Mở Browser: `http://<IP_MAY_CHU>`
- Đăng nhập: `superadmin` / `TempPass@2026`.
- Bảng Dashboard 6 Widgets load bình thường (Báo cáo SLA, License).

**3. Khám Nghiệm Background Jobs (SLA / Partitioning):**
Xem tiến trình Celery quét định kỳ:
```bash
docker compose -f docker-compose.prod.yml logs celery_beat -f
```

---

## 6. Sổ Tay Chữa Cháy (Troubleshooting)

> [!CAUTION]
> Dưới đây là cách đối phó với Bug sụp nền tảng hoặc sai biệt môi trường Staging.

### 🔴 Lỗi: Database Connection Refused (`psycopg.OperationalError`) khi Up Docker
* **Nguyên nhân**: Docker khởi động Backend trước khi Postgres hoàn thiện Boot Log Tables ($< 5s$). Backend vội vã gọi `alembic` (Bước 5) cắm thẳng vào DB $\rightarrow$ Văng Database Refused.
* **Khắc phục**: Chờ 5 - 10 giây cho Healthcheck PostgreSQL xanh lá, rồi mới chạy lại lệnh `docker compose exec backend alembic upgrade head`. 

### 🔴 Lỗi: Trắng Màn Hình Web Hoặc Báo `502 Bad Gateway`
* **Nguyên nhân**: Nginx (Frontend container) không nhìn thấy Backend FastAPI từ cổng 8000, do Backend bị Crash khởi động (Lỗi cú pháp file `.env`).
* **Khắc phục**: 
  1. Check Bug Gunicorn: `docker compose logs backend -f`.
  2. Bổ sung Port hoặc xóa khoảng trắng (Space) nhầm lẫn ở file `.env.prod`. Restart lại `docker compose restart backend`.

### 🔴 Lỗi: Celery Task Nằm Im Đóng Băng / Chậm SLA Escalation
* **Nguyên nhân**: RabbitMQ/Redis Broker rớt Packets hoặc quá tải Queue do số lượng Ticket lớn ứ đọng.
* **Khắc phục**: Cấp cứu Scale-up tăng thêm lực lượng giải quyết Queue theo chiều ngang:
  `docker compose -f docker-compose.prod.yml up -d --scale celery_worker=3`

### 🔴 Lỗi: Agent gửi Report nhưng Device không thấy lọt vào System
* **Nguyên nhân**: SAI MỤC TIÊU ROUTING. Router Backend được quy ước chặn cứng theo Authorization Headers (Token) và Firewall UFW.
* **Khắc phục**: Kiểm tra lại UFW đã mở port `8000` Ingress. Phân quyền API Token của Agent trên Dashboard Admin.

---

## 7. Giải Cứu / Hard Reset Vùng Staging

Nếu môi trường thử nghiệm bị đổ nhầm dữ liệu sai cấu trúc hoặc đứt gãy Database nặng nề, MỆNH LỆNH TEARDOWN hoàn toàn hệ thống:

```bash
# 1. Tạm Ngừng Toàn Bộ Chiến Tuyến
docker compose -f docker-compose.prod.yml down

# 2. Tiêu Hủy Gốc Rễ Database / Cache / Media (CẢNH BÁO DATA SẼ XÓA SẠCH VĨNH VIỄN!)
docker volume rm citms_postgres_data citms_redis_data

# 3. Kích Hoạt Lại Chế Độ Phục Sinh Mới Tinh Tươm 
docker compose -f docker-compose.prod.yml up -d --build
# --> Chạy lại tuần tự từ Bước 5 (Alembic)
```
