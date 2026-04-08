# CITMS 3.6 - Deployment & CI/CD Guide

Hệ thống CITMS 3.6 được thiết kế để triển khai hiện đại, hỗ trợ container hóa hoàn toàn và quy trình CI/CD tự động với chiến lược Blue-Green Deployment.

## 1. Yêu cầu hệ thống (Production)
- **OS**: Ubuntu 22.04 LTS (Khuyên dùng)
- **CPU**: 4 Cores+
- **RAM**: 8GB+
- **Disk**: 100GB SSD+
- **Software**: Docker 24+, Docker Compose 2.20+, Ansible 2.15+

## 2. Cấu trúc Docker
Hệ thống sử dụng Multi-stage Dockerfile (`backend/Dockerfile`) để tối ưu kích thước image:
- **api**: Chạy FastAPI server (Uvicorn).
- **worker**: Chạy Celery worker xử lý tác vụ ngầm.
- **beat**: Chạy Celery beat lập lịch báo cáo.

## 3. Triển khai nhanh với Docker Compose
```bash
# 1. Clone dự án
git clone https://github.com/citms/citms-3.6.git
cd citms-3.6

# 2. Cấu hình môi trường
cp .env.example .env
# Chỉnh sửa các biến DATABASE_URL, REDIS_URL, SECRET_KEY, v.v.

# 3. Khởi động toàn bộ stack
docker-compose up -d --build
```

## 4. Tự động hóa với Ansible
Để provision một server mới từ xa:
```bash
cd ansible
# Cập nhật inventory.ini với IP server của bạn
ansible-playbook -i inventory.ini provision.yml -u root
```

## 5. Quy trình CI/CD (GitLab)
Pipeline được cấu hình trong `.gitlab-ci.yml` bao gồm 3 giai đoạn:
1.  **Build**: Build Docker images cho Backend và Frontend, sau đó push lên Private Registry.
2.  **Test**: Chạy bộ test suite (pytest) trong môi trường container cô lập.
3.  **Deploy (Blue-Green)**:
    -   Xác định môi trường đang hoạt động (Blue hoặc Green).
    -   Deploy phiên bản mới vào môi trường còn lại.
    -   Kiểm tra Health Check.
    -   Chuyển traffic Nginx sang môi trường mới (Zero-downtime).
    -   Cập nhật cờ trạng thái và dừng môi trường cũ.

## 6. Giám sát & Logs
- **Logs**: `docker-compose logs -f api`
- **Metrics**: Tích hợp sẵn OpenTelemetry, có thể kết nối với Prometheus/Grafana.
- **Health Check**: Endpoint `/api/v1/health` trả về trạng thái của DB, Redis và MinIO.

## 7. Backup & Restore
- **Database**: `docker exec citms_db pg_dump -U citms_user citms_db > backup.sql`
- **Media (MinIO)**: Backup thư mục `/data` trong volume `minio_data`.
