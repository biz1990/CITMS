# CITMS 3.6 - Testing Strategy

Hệ thống CITMS 3.6 áp dụng chiến lược kiểm thử đa tầng (Pyramid Testing) để đảm bảo độ tin cậy, hiệu năng và khả năng mở rộng cho 10.000+ agents.

## 1. Cấu trúc Kiểm thử (Testing Pyramid)

### 1.1 Unit Tests (60%)
- **Mục tiêu**: Kiểm tra logic nghiệp vụ cô lập (Services, Models, Utils).
- **Công cụ**: `pytest`, `pytest-asyncio`, `unittest.mock`.
- **Phạm vi**: SLA calculations, State Machine transitions, License logic.

### 1.2 Integration Tests (30%)
- **Mục tiêu**: Kiểm tra sự tương tác giữa các module và Database.
- **Công cụ**: `pytest`, `httpx` (Async client), `Testcontainers` (PostgreSQL/Redis).
- **Phạm vi**: API Endpoints, Repository queries, Celery task execution.

### 1.3 E2E Tests (10%)
- **Mục tiêu**: Kiểm tra luồng nghiệp vụ hoàn chỉnh từ Frontend đến Backend.
- **Công cụ**: `Playwright` (Frontend), `pytest` (Backend API flow).
- **Phạm vi**: Login -> Ingest -> Dashboard -> Ticket -> Report.

## 2. Các kịch bản kiểm thử đặc biệt (Specialized Cases)

### 2.1 Concurrent License Assignment (Pessimistic Locking)
- **Kịch bản**: 100 requests đồng thời cố gắng gán license cho 100 thiết bị khác nhau khi chỉ còn 1 slot trống.
- **Kỳ vọng**: Chỉ 1 request thành công, 99 requests còn lại nhận lỗi `409 Conflict` hoặc `Insufficient Licenses`. Database phải đảm bảo không bị "over-allocation".

### 2.2 Inventory FULL_REPLACE Logic
- **Kịch bản**: Agent gửi bản tin `FULL_REPLACE` chứa 5 phần mềm. Trước đó thiết bị có 10 phần mềm.
- **Kỳ vọng**: Sau khi xử lý, thiết bị chỉ còn đúng 5 phần mềm mới. 5 phần mềm cũ không có trong bản tin phải bị xóa (Soft delete hoặc Hard delete tùy cấu hình).

### 2.3 SLA Calculation Accuracy
- **Kịch bản**: Ticket tạo lúc 16:00 Thứ 6, SLA 4h làm việc. Giờ làm việc kết thúc lúc 17:00.
- **Kỳ vọng**: SLA deadline phải rơi vào 11:00 sáng Thứ 2 tuần tới (bỏ qua Thứ 7, Chủ Nhật và giờ nghỉ).

### 2.4 State Machine Transitions
- **Kịch bản**: Thử chuyển Ticket từ `OPEN` sang `RESOLVED` mà không qua `IN_PROGRESS`.
- **Kỳ vọng**: Hệ thống từ chối transition và trả về lỗi `Invalid State Transition`.

## 3. Load Testing (10.000 Agents)
- **Công cụ**: `Locust`.
- **Kịch bản**: 
  - 10.000 users giả lập gửi bản tin Ingest mỗi 30 phút.
  - Tần suất: ~5.5 requests/giây (RPS) trung bình, với đỉnh điểm (Spike) lên tới 50 RPS.
- **KPI**: 
  - Response time (p95) < 200ms cho Ingest API.
  - Tỷ lệ lỗi < 0.1%.

## 4. CI/CD Integration
- Toàn bộ Unit & Integration tests được chạy tự động trong GitLab CI/CD stage `test`.
- Coverage report được xuất ra định dạng XML và hiển thị trực tiếp trên Merge Request.
- Ngưỡng (Threshold) tối thiểu: **80%**.
