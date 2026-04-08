# CITMS 3.6 Backend - Core Structure

## Cấu trúc thư mục (DDD Modular Monolith)
```
backend/
├── alembic/              # Database migrations
├── src/
│   ├── core/             # Core settings, security, exceptions, OTEL, Celery
│   ├── infrastructure/   # Database, Redis, Base models/repos
│   │   ├── models/       # SQLAlchemy models
│   │   └── repositories/ # Data access layer
│   ├── application/      # Application services (cross-context logic)
│   ├── domain/           # Shared domain logic & entities
│   ├── interfaces/       # Shared interfaces/DTOs (Pydantic)
│   ├── contexts/         # Bounded Contexts (Modules)
│   │   ├── auth/         # Authentication & RBAC
│   │   ├── asset/        # Asset & Inventory
│   │   ├── itsm/         # ITSM & Ticket
│   │   └── procurement/  # Procurement & Warehouse
│   └── main.py           # FastAPI entry point
├── alembic.ini           # Alembic config
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variables template
└── README_backend.md     # Backend documentation
```

## Hướng dẫn chạy Local

### 1. Cài đặt môi trường ảo
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# hoặc
venv\Scripts\activate     # Windows
```

### 2. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 3. Cấu hình Database & Redis
Tạo file `.env` từ `.env.example` và cập nhật thông tin kết nối PostgreSQL và Redis.

### 4. Chạy Migrations
```bash
alembic upgrade head
```

### 5. Chạy Server
```bash
uvicorn src.main:app --reload --port 8000
```

### 6. Chạy Celery Worker
```bash
celery -A src.core.celery worker --loglevel=info
```

## API Standards
- **Error Handling**: Tuân thủ RFC 7807.
- **Tracing**: Tích hợp OpenTelemetry (Trace-ID trả về trong Header).
- **Concurrency**: Sử dụng Optimistic Locking (`version` column).
- **Soft-delete**: Tự động lọc các bản ghi có `deleted_at IS NULL`.
