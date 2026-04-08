# Hướng dẫn Triển khai CITMS 3.6 trên Máy Tính Cục Bộ (Local)

Đây là tài liệu hướng dẫn nhanh gọn, dễ hiểu dành cho lập trình viên và người dùng muốn tự cài đặt hệ thống CITMS 3.6 trên máy cá nhân (Windows, Ubuntu, hoặc Mac) để thử nghiệm và phát triển. 

Tài liệu này không yêu cầu đăng ký tên miền hay cấu hình SSL/Nginx phức tạp. Nội dung hoàn toàn sử dụng **Docker Compose** và **Localhost**.

---

## 1. Chuẩn bị Ban Đầu

**Yêu cầu Phần cứng Tối thiểu:**
- RAM: Tối thiểu 8GB (khuyên dùng 16GB)
- CPU: Intel Core i5 / AMD Ryzen 5 hoặc tương đương.
- Ổ cứng: Trống ít nhất 10GB.

**Yêu cầu Phần mềm:**
Nếu đang dùng **Windows**:
1. Cài đặt [Docker Desktop](https://www.docker.com/products/docker-desktop/). Hãy đảm bảo WSL2 (Windows Subsystem for Linux) đã được bật trong lúc cài Docker.
2. Cài đặt [Git](https://git-scm.com/download/win).
3. Cài đặt [Node.js](https://nodejs.org/) (phiên bản > 20.0).

Nếu đang dùng **Ubuntu/Linux**:
1. Cài đặt Docker (`sudo apt install docker.io`) và docker-compose.
2. Cài đặt Git & Node.js 20+.

---

## 2. Tải Mã Nguồn

Mở Terminal (trên Ubuntu) hoặc Command Prompt / PowerShell (trên Windows), điều hướng tới thư mục muốn lưu trữ và chạy lệnh:

```bash
git clone https://github.com/your-repo/citms.git
cd citms
```
*(Nếu kho lưu trữ đổi sang link khác, hãy điền link git dự án CITMS của bạn vào URL tải)*

---

## 3. Cấu hình Biến Môi trường (`.env`)

Tại thu mục gốc của dự án, bạn sẽ thấy file `.env.example`. Hãy copy và đổi tên thành `.env` để cấu hình thông tin.

**Lập trình viên và Tester, bạn chỉ cần một số cấu hình đơn giản để chạy cục bộ.**

```bash
cp .env.example .env
```
Mở file `.env` bằng bất kỳ trình soạn thảo văn bản nào (như VSCode, Notepad), cấu hình các thông số như sau:

```ini
ENVIRONMENT=development
PROJECT_NAME="CITMS v3.6 Local"
API_V1_STR=/api/v1
SECRET_KEY="local_secret_key_super_secure_string_123"

# DATABASE (Local)
POSTGRES_SERVER=db
POSTGRES_PORT=5432
POSTGRES_DB=citms_local_db
POSTGRES_USER=admin
POSTGRES_PASSWORD=admin

SQLALCHEMY_DATABASE_URI=postgresql+asyncpg://admin:admin@db:5432/citms_local_db
SYNC_DATABASE_URI=postgresql://admin:admin@db:5432/citms_local_db

# REDIS (Local)
REDIS_HOST=redis
REDIS_PORT=6379
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# MINIO STORAGE
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin
S3_ENDPOINT=http://minio:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET_NAME=citms-attachments
S3_REGION=ap-southeast-1
```

---

## 4. Khởi chạy Hệ thống Bằng Docker Compose

CITMS chứa sẵn cấu hình `docker-compose.yml` gồm toàn bộ: PostgreSQL, Redis, MinIO, API (FastAPI) và Worker (Celery).

**Bước 4.1: Chạy Database và Storage trước**
```bash
docker compose up -d db redis minio
```
> **Chờ khoảng 20 giây** để Database PostgreSQL khởi tạo hoàn chỉnh lần đầu.

**Bước 4.2: Chạy Backend API và Background Workers**
```bash
docker compose up -d api worker event_worker
```
> *Lệnh `-d` giúp chạy Container ở chế độ ngầm (Background).*

---

## 5. Khởi tạo Database & Super Admin

Dù các Containers đã chạy lên, Database vẫn đang... trống trơn. Bạn cần chạy cấu hình bảng và dữ liệu mồi.

**Bước 5.1: Chạy Alembic để khởi tạo các bảng (Tables)**
```bash
docker exec -it <tên_container_api> alembic upgrade head
```
*(Tips: Tên container API có thể tra cứu bằng lệnh `docker ps`. Thông thường nó có tên `citms-api-1` hoặc tương tự.)*

**Bước 5.2: Chèn dữ liệu mồi (Seed Data)**
Hệ thống cần các danh mục thiết bị, quyền, vai trò mặc định...
```bash
docker exec -it <tên_container_api> python backend/scripts/seed_initial_data.py
```

**Bước 5.3: Tạo tài khoản Đăng Nhập Đầu Tiên (Super Admin)**
```bash
docker exec -it <tên_container_api> python backend/scripts/create_super_admin.py --email admin@local.com --password admin
```

---

## 6. Chạy Frontend (React)

Thay vì chạy qua Nginx, ta dùng Dev Server thông thường của Vite để dễ theo dõi sự thay đổi khi code Frontend.

Mở một Terminal/PowerShell thứ 2 (hoặc mở Tab mới), cd vào thư mục root dự án của bạn (nếu source code frontend nằm ở `./src` theo cấu trúc chung):

```bash
# Đảm bảo bạn đang ở thư mục gốc chứa package.json
# Cài đặt thư viện:
npm install

# (tuỳ chọn) Sao chép cấu hình Frontend:
cp .env.example .env  # Đảm bảo VITE_API_URL=http://localhost:8000/api/v1

# Chạy Frontend Server:
npm run dev
```

Server sẽ khởi động và cung cấp link cho bạn, thường là: `http://localhost:5173`.

---

## 7. Kiểm tra Hệ thống Hoạt động

Mở trình duyệt Web (Chrome, Edge...) và kiểm tra theo danh sách:

1. **Giao diện người dùng (React Frontend):** `http://localhost:5173`
   - Đăng nhập thử với `admin@local.com` và pass `admin` (vừa tạo ở bước 5.3).
2. **Swagger Backend API (Tài liệu API):** `http://localhost:8000/docs`
   - Có thể dùng giao diện này để test thử các API Endpoint.
3. **Quản trị Storage MinIO:** `http://localhost:9001`
   - Tài khoản đăng nhập được tạo ở phần `.env` là `minioadmin` và pass `minioadmin`.
   - Sau khi vào, nhớ tạo Bucket mang tên `citms-attachments` và đặt Access Mode là Public để test ảnh upload từ React.

---

## 8. Các Lệnh Hữu Ích

Khi phát triển, có thể bạn sẽ hay dùng những lệnh này:

**Xem log hệ thống (Ví dụ API Container):**
```bash
docker compose logs -f api
```

**Biên dịch lại Server Backend nếu có thay đổi trong `backend/`:**
```bash
docker compose build api
```

**Khởi động lại một dịch vụ cụ thể (Ví dụ: `worker`):**
```bash
docker compose restart worker
```

**Dừng lại mọi Container nhưng giữ nguyên dữ liệu chưa xoá:**
```bash
docker compose stop
```

---

## 9. Troubleshooting Phổ Biến

**1. Lỗi Cổng bị trùng (Port already in use)**
- Triệu chứng: Không chạy được `docker compose up -d db` báo lỗi port `5432` đang bị chiếm.
- Cách sửa: Khả năng máy tính của bạn đã cài sẵn phần mềm Postgres. Hãy tạm dừng service Postgres của máy tính, hoặc đổi thông số `POSTGRES_PORT` trong file `.env` qua `5435` chẳng hạn (nhớ đổi tương ứng tại file `docker-compose.yml`!).

**2. Lỗi Backend hiển thị CORS Error từ Frontend**
- Triệu chứng: Chạy React, đăng nhập không tác dụng, F12 console đỏ rực lỗi CORS.
- Cách sửa: Mở file `.env` của hệ thống Backend, thêm `BACKEND_CORS_ORIGINS=["http://localhost:5173"]`. Sau đó khởi động lại API: `docker compose restart api`.

**3. Lệnh Migration `docker exec` báo lỗi container không tồn tại**
- Triệu chứng: Viết sai tên Container.
- Cách sửa: Chạy `docker ps` để xem đúng chính xác tên Container (Cột NAMES). Đôi khi docker desktop tự thêm prefix thư mục ví dụ `citms_api_1`.

---

## 10. Cách Dừng & Xóa Dữ Liệu Test (Clean Up)

Nếu bạn muốn xóa sạch mọi thứ để khởi tạo lại từ đầu như một chiếc hộp rỗng (xóa trắng Database và File cache).

```bash
# Xóa Container
docker compose down

# Xóa KHÔNG THƯƠNG TIẾC (Xóa luôn Database, Volume và Image đang treo)
docker compose down -v
```

Để chắc chắn, bạn có thể chạy thêm `docker system prune` nếu ổ cứng hết chỗ. Tới đây bạn có thể vòng lại Bước 4 để bắt đầu khởi tạo lại môi trường sạch sẽ mới.
