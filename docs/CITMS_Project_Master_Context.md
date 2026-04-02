# CITMS - Centralized IT Management System  
**Master Project Context & Full History**  
**Phiên bản:** 3.0 (Production-Ready Spec)  
**Ngày cập nhật:** 01/04/2026  
**Tác giả:** Nguyen Trung Hau  
**Trạng thái:** Đã hoàn thành 6 Phase cơ bản, đang chuyển AI Agent

## 1. Giới thiệu Dự án
CITMS là hệ thống quản lý IT All-in-One theo mô hình Modular Monolith + Domain-Driven Design (DDD), được xây dựng để thay thế hoàn toàn các hệ thống phân mảnh hiện tại (GLPI + Excel).

Hệ thống quản lý toàn diện vòng đời tài sản IT theo chuẩn **ITIL 4**, bao gồm:
- Đề xuất mua → Nhập kho → Cấp phát → Bảo trì → Thu hồi → Thanh lý
- Giám sát hạ tầng tự động qua GLPI Agent
- ITSM (Incident, Problem, Change Management)
- Quản lý bản quyền phần mềm (có xử lý install/uninstall)
- Hỗ trợ đặc biệt thiết bị Zebra wireless scanner (multi-docking) và thiết bị dùng cổng COM/Hybrid

## 2. Tài liệu SRS Chính thức
Toàn bộ yêu cầu hệ thống được mô tả chi tiết trong **Software Requirements Specification (SRS) phiên bản 3.0**.  
AI Agent mới phải tuân thủ **100%** nội dung SRS này, không được simplify hoặc bỏ qua bất kỳ yêu cầu nào.

**Các phần quan trọng nhất cần nắm vững:**
- Section 1: Tổng quan, 11 Core Modules, mục tiêu kinh doanh
- Section 3: Database Schema (toàn bộ bảng, cột, relationship, trigger, partitioning, DEFERRABLE FK, version column, soft delete)
- Section 4: Business Logic (đặc biệt: Inventory Ingestion, Zebra docking, COM port, License uninstall trigger, State Machine, SLA & Escalation)
- Section 5: API Endpoints (bao gồm /inventory/report)
- Section 6: RBAC Matrix chi tiết
- Section 7: SLA Table & Escalation Rules
- Section 8: Reports & Export (9 báo cáo, scheduled report, export Excel/PDF)
- Section 11: Deployment & CI/CD (Docker, Blue-Green, Ansible)

## 3. Công nghệ Stack (Tech Stack)
- **Backend:** FastAPI (Python 3.11+), SQLAlchemy 2.0, Alembic
- **Frontend:** React 18 + TypeScript + Ant Design Pro + React Flow + PWA
- **Database:** PostgreSQL 16 (Partitioning, JSONB, Triggers, DEFERRABLE FK)
- **Cache & Queue:** Redis 7
- **Storage:** MinIO (S3 compatible)
- **Background Jobs:** Celery + Redis
- **Deployment:** Docker + Docker Compose (sau này có thể dùng Ansible)

## 4. Tiến độ đã hoàn thành (6 Phase)

- **Phase 0:** Project setup, docker-compose.yml, cấu trúc thư mục modular, .env.example
- **Phase 1:** Database Layer – Toàn bộ SQLAlchemy models + Alembic migrations (đã có trigger license, partitioning history_logs, DEFERRABLE FK)
- **Phase 2:** Core Services & Business Logic (Auth, Inventory Ingestion, License, Asset, ITSM, Notification, Workflow)
- **Phase 3:** API Layer – Các router chính, RBAC dependency, X-Request-ID, error handling
- **Phase 4:** Background Tasks (Celery) – Notification, scheduled reports, SLA escalation
- **Phase 5:** Frontend – Dashboard, Device Detail (5 tabs), Kanban, React Flow topology
- **Phase 6:** Testing, Docker refinement, CI/CD template

**Hiện trạng:** Đã hoàn thành nền tảng chính. Module 8 (Reports & Export) cần được nâng cấp lên mức chi tiết cao hơn (RAM chi tiết theo slot, phần mềm theo từng máy, Office 365 vs Office 2021…).

## 5. Yêu cầu quan trọng với AI Agent mới (GLM 5.0)

Từ bây giờ, bạn là AI Agent chính thức tiếp tục dự án. Hãy tuân thủ nghiêm ngặt các nguyên tắc sau:

1. **Luôn tham chiếu SRS phiên bản 3.0** trước khi thực hiện bất kỳ tính năng nào.
2. Không simplify business logic, đặc biệt là:
   - Reconciliation logic của GLPI Agent
   - Xử lý Zebra wireless multi-docking
   - License uninstall sử dụng Database Trigger
   - Optimistic locking với cột `version`
3. Module 8 cần được triển khai chi tiết:
   - Báo cáo RAM theo hãng, dung lượng, slot
   - Thống kê phần mềm (số máy chạy Office 365, Office 2021…)
   - Export Excel/PDF
   - Scheduled report bằng Celery Beat
4. Giữ nguyên phong cách code sạch, có comment, và tuân thủ cấu trúc đã thiết lập.

## 6. Hướng dẫn làm việc tiếp theo
Khi tôi đưa ra yêu cầu mới, bạn phải:
- Xác nhận bạn đã hiểu yêu cầu theo SRS
- Đề xuất kế hoạch thực hiện (nếu cần)
- Triển khai code hoặc tài liệu
- Sau khi xong, tóm tắt những gì đã làm và chờ confirm

---

**File này là "bộ não" của dự án.**  
Mọi AI Agent làm việc với CITMS đều phải đọc và hiểu toàn bộ nội dung file này trước khi thực hiện bất kỳ nhiệm vụ nào.

**Kết thúc Master Context**