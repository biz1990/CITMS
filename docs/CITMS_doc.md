**TÀI LIỆU ĐẶC TẢ HỆ THỐNG QUẢN LÝ IT TẬP TRUNG (CITMS)**  
**Centralized IT Management System**  

**Phiên bản:** 3.0 (Production-Ready Spec – Architecturally Sealed & Fully Completed)  
**Ngày:** 30/03/2026  
**Tác giả:** Nguyen Trung Hau / Bộ phận IT  
**Reviewer:** DBA Admin + Tech Lead + Kiến trúc sư Dự án  
**Trạng thái:** ĐÃ HOÀN THIỆN TOÀN DIỆN – SẴN SÀNG TRIỂN KHAI CODE  

---

## 1. TỔNG QUAN DỰ ÁN

### 1.1. Mục tiêu
Xây dựng một nền tảng quản lý IT All-in-One duy nhất, theo mô hình Modular Monolith kết hợp Domain-Driven Design (DDD), nhằm loại bỏ hoàn toàn sự phân mảnh dữ liệu giữa các hệ thống hiện tại.  

Hệ thống phải quản lý toàn diện vòng đời tài sản IT (Asset Lifecycle) theo chuẩn ITIL 4, bao gồm các giai đoạn sau:  
- Đề xuất mua sắm → Phê duyệt → Nhập kho → Cấp phát → Giám sát & Bảo trì → Thu hồi → Thanh lý.  
- Tích hợp giám sát hạ tầng tự động qua GLPI Agent.  
- Quản lý nghiệp vụ ITSM (Incident, Problem, Change Management, Request).  
- Quản lý bản quyền phần mềm, phát hiện vi phạm và tuân thủ license (bao gồm cả quá trình cài đặt và gỡ cài đặt).  
- Hỗ trợ kiểm kê vật lý qua Mobile PWA (offline-first).  
- Hỗ trợ đặc biệt các thiết bị công nghiệp phổ biến tại công ty: Máy scan Zebra không dây (multi-docking), máy scan/máy in sử dụng cổng COM (Serial Port) và hybrid USB+COM.

Mục tiêu kinh doanh cụ thể:  
- Tăng tốc độ xử lý yêu cầu IT ít nhất 40%.  
- Giảm thời gian downtime tài sản xuống dưới 4 giờ/tháng.  
- Đảm bảo tỷ lệ tuân thủ license đạt 100%.  
- Cung cấp báo cáo thời gian thực, lịch sử audit chi tiết và dashboard trực quan cho lãnh đạo.

### 1.2. Phạm vi chức năng (11 Core Modules)
1. Asset & Inventory Management (thu thập tự động, topology, linh kiện, CMDB).  
2. Remote Control (tích hợp RustDesk trực tiếp trên giao diện).  
3. ITSM (phiếu bảo trì, lịch sử, thay linh kiện, Change Management đầy đủ).  
4. Procurement & Warehouse (đề xuất mua, duyệt, nhập/xuất kho, vật tư tiêu hao).  
5. Onboarding/Offboarding (quy trình cấp/thu hồi có approval workflow).  
6. Auth & RBAC (xác thực đa phương thức, phân quyền theo chuẩn RBAC với bảng roles riêng).  
7. Notification Engine (12+ loại cảnh báo đa kênh).  
8. Reports & Export (9 báo cáo chuẩn + TCO + scheduled).  
9. License & Compliance Management (phát hiện vi phạm tự động, hỗ trợ uninstall).  
10. Audit Trail & History (ghi log mọi thao tác với X-Request-ID).  
11. Physical Inventory & Barcode/QR (kiểm kê di động qua PWA).

**Ngoài phạm vi (Out of Scope ở Phase 1):**  
- Tích hợp trực tiếp với hệ thống HR (sẽ mở rộng Phase 2 qua API).  
- Quản lý mạng chi tiết (switch config, VLAN).  
- Tích hợp với hệ thống giám sát mạng (PRTG/Zabbix) – chỉ hỗ trợ qua Agent.

### 1.3. Giả định & Phụ thuộc (Assumptions & Dependencies)
- Mạng LAN/WiFi nội bộ ổn định, Agent có thể kết nối HTTPS đến CITMS.  
- RustDesk server được tự host hoặc sử dụng phiên bản cloud có hỗ trợ webhook.  
- Có sẵn domain/email server (SMTP) để gửi thông báo.  
- Tài khoản nhân sự đã tồn tại trên LDAP/Active Directory hoặc Local.  
- Công ty sử dụng nhiều máy scan Zebra không dây và thiết bị COM port.  
- Server chính chạy trên môi trường on-premise hoặc private cloud (MinIO + PostgreSQL).

### 1.4. Rủi ro & Giải pháp giảm thiểu (Risks & Mitigation)
- Rủi ro Agent gửi dữ liệu dồn (flood): Giải pháp: Idempotency key (inventory_run_id) + Rate limiting + Redis lock.  
- Rủi ro xung đột dữ liệu Agent vs Manual: Giải pháp: Reconciliation UI + manual override + audit log.  
- Rủi ro vi phạm bản quyền: Giải pháp: Auto-detect + tạo ticket CRITICAL + alert.  
- Rủi ro mất dữ liệu backup: Giải pháp: Geo-redundant S3 + RPO < 6 giờ.  
- Rủi ro thay đổi Role: Giải pháp: Đã tách bảng roles + user_roles.  
- Rủi ro sai used_seats license khi gỡ phần mềm: Giải pháp: Dùng Database Trigger kết hợp logic trừ đúng license_id đã gắn; alert nếu NULL.  
- Rủi ro Circular FK (User - Department): Giải pháp: Sử dụng DEFERRABLE INITIALLY DEFERRED cho FK manager_id.  
- Rủi ro ghi đè dữ liệu khi nhiều người cùng sửa: Giải pháp: Áp dụng Optimistic Locking (cột version) ở cấp độ Backend & Database cho các bảng Ticket và Device.

---

## 2. KIẾN TRÚC HỆ THỐNG & CÔNG NGHỆ (C4 MODEL)

### 2.1. Kiến trúc Context & Container
- **Level 1 - Context:** CITMS giao tiếp với Người dùng (Web/Mobile PWA), GLPI Agent, RustDesk Server, LDAP/AD, SMTP Server.  
- **Level 2 - Container:**  
  - Web Client: React PWA hosted trên Nginx.  
  - Backend API: FastAPI chạy Gunicorn/Uvicorn.  
  - Background Jobs: Celery Workers.  
  - Database: PostgreSQL 16 (Primary) + Read Replica.  
  - Cache/Broker: Redis 7.  
  - Storage: MinIO (S3).

### 2.2. Kiến trúc Component (C4 Level 3 - Backend DDD)
Backend được chia thành các Context độc lập:  
- AuthContext: Xử lý đăng nhập, JWT, đồng bộ LDAP.  
- AssetContext: Quản lý devices, components, topology mapping.  
- ITSMContext: Quản lý ticket, maintenance, tính toán SLA, escalation.  
- ProcurementContext: Quản lý PO, nhập xuất kho, nhà cung cấp.  
- InventoryIngestionContext: Nhận dữ liệu thô từ Agent, reconcile, phân loại Zebra/COM.  

Các Context giao tiếp với nhau qua Redis Pub/Sub (ví dụ: AssetContext phát sự kiện LICENSE_VIOLATED → ITSMContext tự động tạo ticket CRITICAL).

---

## 3. THIẾT KẾ CƠ SỞ DỮ LIỆU (DATABASE SCHEMA) – CHI TIẾT TOÀN BỘ

**Quy ước chung cho TẤT CẢ các bảng:**  
- id: UUID v4 (PRIMARY KEY DEFAULT uuid_generate_v4()).  
- created_at, updated_at: TIMESTAMPTZ (NOT NULL, default NOW()).  
- deleted_at: TIMESTAMPTZ (nullable, Soft Delete).  
- Mọi query Backend mặc định thêm WHERE deleted_at IS NULL.  
- Partial Unique Index cho tất cả trường unique.  
- Index trên mọi FK và cột filter thường dùng.  
- Trigger tự động cập nhật updated_at trước mỗi UPDATE.  
- Optimistic Locking: Các bảng có nguy cơ cập nhật đồng thời cao (tickets, devices, purchase_orders) sẽ có thêm cột version INT DEFAULT 1. Mọi logic UPDATE phải kèm điều kiện WHERE version = ? và tăng lên version + 1. Nếu ảnh hưởng 0 dòng → Ném lỗi HTTP 409 Conflict.

### 3.1. Bảng Nhân sự & Tổ chức
**roles**  
- id (UUID PRIMARY KEY DEFAULT uuid_generate_v4())  
- name (VARCHAR(50) UNIQUE NOT NULL)  
- description (TEXT)  
- created_at (TIMESTAMPTZ DEFAULT NOW())  
- updated_at (TIMESTAMPTZ DEFAULT NOW())  
- deleted_at (TIMESTAMPTZ)  

**user_roles**  
- id (UUID PRIMARY KEY DEFAULT uuid_generate_v4())  
- user_id (UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE)  
- role_id (UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE)  
- assigned_at (TIMESTAMPTZ DEFAULT NOW())  
- assigned_by (UUID REFERENCES users(id))  
- UNIQUE(user_id, role_id)  

**users**  
- id (UUID PRIMARY KEY DEFAULT uuid_generate_v4())  
- username (VARCHAR(50) UNIQUE NOT NULL)  
- email (VARCHAR(100) UNIQUE NOT NULL)  
- password_hash (VARCHAR(255))  
- full_name (VARCHAR(100))  
- employee_id (VARCHAR(20) UNIQUE)  
- department_id (UUID REFERENCES departments(id))  
- is_active (BOOLEAN DEFAULT TRUE)  
- last_login (TIMESTAMPTZ)  
- auth_provider (ENUM: LOCAL, LDAP, SSO)  
- preferences (JSONB DEFAULT '{}')  
- created_at (TIMESTAMPTZ DEFAULT NOW())  
- updated_at (TIMESTAMPTZ DEFAULT NOW())  
- deleted_at (TIMESTAMPTZ)  

**departments**  
- id (UUID PRIMARY KEY DEFAULT uuid_generate_v4())  
- name (VARCHAR(100) NOT NULL)  
- parent_id (UUID REFERENCES departments(id))  
- manager_id (UUID)  
- level (SMALLINT)  
- created_at (TIMESTAMPTZ DEFAULT NOW())  
- updated_at (TIMESTAMPTZ DEFAULT NOW())  
- deleted_at (TIMESTAMPTZ)  

### 3.2. Bảng Vị trí & Hạ tầng
**locations**  
- id (UUID PRIMARY KEY DEFAULT uuid_generate_v4())  
- name (VARCHAR(100) NOT NULL)  
- parent_id (UUID REFERENCES locations(id))  
- location_code (VARCHAR(20) UNIQUE)  
- is_active (BOOLEAN DEFAULT TRUE)  
- created_at (TIMESTAMPTZ DEFAULT NOW())  
- updated_at (TIMESTAMPTZ DEFAULT NOW())  
- deleted_at (TIMESTAMPTZ)  

### 3.3. Bảng Tài sản
**devices**  
- id (UUID PRIMARY KEY DEFAULT uuid_generate_v4())  
- asset_tag (VARCHAR(50))  
- name (VARCHAR(100))  
- device_type (VARCHAR(50))  
- device_subtype (VARCHAR(30))  
- manufacturer (VARCHAR(100))  
- model (VARCHAR(100))  
- serial_number (VARCHAR(100))  
- uuid (VARCHAR(36))  
- primary_mac (VARCHAR(17))  
- hostname (VARCHAR(100))  
- network_ipv4 (INET)  
- os_name (VARCHAR(50))  
- os_version (VARCHAR(50))  
- status (VARCHAR(30))  
- assigned_to_id (UUID REFERENCES users(id))  
- location_id (UUID REFERENCES locations(id))  
- purchase_item_id (UUID REFERENCES purchase_items(id))  
- purchase_date (DATE)  
- purchase_cost (DECIMAL(12,2))  
- depreciation_method (VARCHAR(20))  
- rustdesk_id (VARCHAR(50))  
- rustdesk_password_enc (BYTEA)  
- last_seen (TIMESTAMPTZ)  
- warranty_expire_date (DATE)  
- warranty_provider_id (UUID REFERENCES vendors(id))  
- com_port (VARCHAR(20))  
- dock_serial (VARCHAR(100))  
- version (INTEGER DEFAULT 1)  
- notes (TEXT)  
- invalid_serial (BOOLEAN DEFAULT FALSE)  
- created_at (TIMESTAMPTZ DEFAULT NOW())  
- updated_at (TIMESTAMPTZ DEFAULT NOW())  
- deleted_at (TIMESTAMPTZ)  

**device_components**  
- id (UUID PRIMARY KEY DEFAULT uuid_generate_v4())  
- device_id (UUID REFERENCES devices(id))  
- component_type (VARCHAR(50))  
- serial_number (VARCHAR(100))  
- model (VARCHAR(100))  
- manufacturer (VARCHAR(100))  
- specifications (JSONB)  
- slot_name (VARCHAR(50))  
- is_internal (BOOLEAN)  
- installation_date (DATE)  
- removed_date (DATE)  
- status (VARCHAR(20))  
- created_at (TIMESTAMPTZ DEFAULT NOW())  
- updated_at (TIMESTAMPTZ DEFAULT NOW())  
- deleted_at (TIMESTAMPTZ)  

**device_connections**  
- id (UUID PRIMARY KEY DEFAULT uuid_generate_v4())  
- source_device_id (UUID NOT NULL REFERENCES devices(id))  
- target_device_id (UUID NOT NULL REFERENCES devices(id))  
- connection_type (VARCHAR(30))  
- port_name (VARCHAR(50))  
- baud_rate (INTEGER)  
- is_active (BOOLEAN DEFAULT TRUE)  
- connected_at (TIMESTAMPTZ)  
- disconnected_at (TIMESTAMPTZ)  
- created_at (TIMESTAMPTZ DEFAULT NOW())  
- updated_at (TIMESTAMPTZ DEFAULT NOW())  
- deleted_at (TIMESTAMPTZ)  

**cmdb_relationships**  
- id (UUID PRIMARY KEY DEFAULT uuid_generate_v4())  
- source_id (UUID NOT NULL REFERENCES devices(id))  
- target_id (UUID NOT NULL REFERENCES devices(id))  
- relationship_type (VARCHAR(50))  
- created_at (TIMESTAMPTZ DEFAULT NOW())  
- updated_at (TIMESTAMPTZ DEFAULT NOW())  
- deleted_at (TIMESTAMPTZ)  
- CONSTRAINT chk_no_self_relation CHECK (source_id != target_id)  

### 3.4. Bảng Kho & Vật tư
**spare_parts_inventory**  
- id (UUID PRIMARY KEY DEFAULT uuid_generate_v4())  
- name (VARCHAR(100) NOT NULL)  
- part_number (VARCHAR(50))  
- category (VARCHAR(30))  
- quantity (INTEGER DEFAULT 0)  
- min_quantity (INTEGER DEFAULT 5)  
- unit_cost (DECIMAL(12,2))  
- total_value (DECIMAL(12,2) GENERATED ALWAYS AS (quantity * unit_cost) STORED)  
- location_id (UUID REFERENCES locations(id))  
- vendor_id (UUID REFERENCES vendors(id))  
- image_url (VARCHAR(500))  
- created_at (TIMESTAMPTZ DEFAULT NOW())  
- updated_at (TIMESTAMPTZ DEFAULT NOW())  
- deleted_at (TIMESTAMPTZ)  

**vendors**  
- id (UUID PRIMARY KEY DEFAULT uuid_generate_v4())  
- name (VARCHAR(100) NOT NULL)  
- contact_person (VARCHAR(100))  
- email (VARCHAR(100))  
- phone (VARCHAR(20))  
- address (TEXT)  
- contract_details (JSONB)  
- rating (SMALLINT CHECK (rating BETWEEN 1 AND 5))  
- created_at (TIMESTAMPTZ DEFAULT NOW())  
- updated_at (TIMESTAMPTZ DEFAULT NOW())  
- deleted_at (TIMESTAMPTZ)  

### 3.5. Bảng Thu mua & Hợp đồng
**purchase_orders**  
- id (UUID PRIMARY KEY DEFAULT uuid_generate_v4())  
- po_code (VARCHAR(30) UNIQUE)  
- title (VARCHAR(200))  
- status (VARCHAR(30) DEFAULT 'DRAFT')  
- requested_by (UUID REFERENCES users(id))  
- approved_by (UUID REFERENCES users(id))  
- total_estimated_cost (DECIMAL(12,2))  
- approved_at (TIMESTAMPTZ)  
- version (INTEGER DEFAULT 1)  
- created_at (TIMESTAMPTZ DEFAULT NOW())  
- updated_at (TIMESTAMPTZ DEFAULT NOW())  
- deleted_at (TIMESTAMPTZ)  

**purchase_items**  
- id (UUID PRIMARY KEY DEFAULT uuid_generate_v4())  
- purchase_order_id (UUID REFERENCES purchase_orders(id))  
- item_name (VARCHAR(100))  
- category (VARCHAR(30))  
- quantity (INTEGER)  
- unit_price (DECIMAL(12,2))  
- specifications (JSONB)  
- received_quantity (INTEGER DEFAULT 0)  
- received_by (UUID REFERENCES users(id))  
- received_at (TIMESTAMPTZ)  
- created_at (TIMESTAMPTZ DEFAULT NOW())  
- updated_at (TIMESTAMPTZ DEFAULT NOW())  
- deleted_at (TIMESTAMPTZ)  

**contracts**  
- id (UUID PRIMARY KEY DEFAULT uuid_generate_v4())  
- contract_code (VARCHAR(30) UNIQUE)  
- vendor_id (UUID REFERENCES vendors(id))  
- contract_type (VARCHAR(30))  
- start_date (DATE)  
- expire_date (DATE)  
- terms (JSONB)  
- created_at (TIMESTAMPTZ DEFAULT NOW())  
- updated_at (TIMESTAMPTZ DEFAULT NOW())  
- deleted_at (TIMESTAMPTZ)  

### 3.6. Bảng Nghiệp vụ ITSM
**tickets**  
- id (UUID PRIMARY KEY DEFAULT uuid_generate_v4())  
- ticket_code (VARCHAR(30) UNIQUE NOT NULL)  
- title (VARCHAR(200) NOT NULL)  
- description (TEXT)  
- status (VARCHAR(30) DEFAULT 'OPEN')  
- priority (VARCHAR(20) DEFAULT 'MEDIUM')  
- category (VARCHAR(50))  
- impact (VARCHAR(20))  
- urgency (VARCHAR(20))  
- is_change (BOOLEAN DEFAULT FALSE)  
- change_type (VARCHAR(50))  
- change_plan (TEXT)  
- rollback_plan (TEXT)  
- cab_approval_status (VARCHAR(20))  
- cab_approved_by (UUID REFERENCES users(id))  
- cab_approved_at (TIMESTAMPTZ)  
- created_by (UUID REFERENCES users(id))  
- assigned_to_id (UUID REFERENCES users(id))  
- device_id (UUID REFERENCES devices(id))  
- location_id (UUID REFERENCES locations(id))  
- vendor_id (UUID REFERENCES vendors(id))  
- estimated_cost (DECIMAL(12,2))  
- actual_cost (DECIMAL(12,2))  
- sla_response_due (TIMESTAMPTZ)  
- sla_resolution_due (TIMESTAMPTZ)  
- resolution_notes (TEXT)  
- due_date (TIMESTAMPTZ)  
- version (INTEGER DEFAULT 1)  
- created_at (TIMESTAMPTZ DEFAULT NOW())  
- updated_at (TIMESTAMPTZ DEFAULT NOW())  
- deleted_at (TIMESTAMPTZ)  

**ticket_comments**  
- id (UUID PRIMARY KEY DEFAULT uuid_generate_v4())  
- ticket_id (UUID REFERENCES tickets(id))  
- user_id (UUID REFERENCES users(id))  
- content (TEXT)  
- is_internal (BOOLEAN)  
- created_at (TIMESTAMPTZ DEFAULT NOW())  
- updated_at (TIMESTAMPTZ DEFAULT NOW())  
- deleted_at (TIMESTAMPTZ)  

**maintenance_logs**  
- id (UUID PRIMARY KEY DEFAULT uuid_generate_v4())  
- device_id (UUID REFERENCES devices(id))  
- ticket_id (UUID REFERENCES tickets(id))  
- action_type (VARCHAR(50))  
- description (TEXT)  
- old_component_details (JSONB)  
- new_component_details (JSONB)  
- performed_by_id (UUID REFERENCES users(id))  
- spare_part_id (UUID REFERENCES spare_parts_inventory(id))  
- quantity_used (INTEGER)  
- cost (DECIMAL(12,2))  
- status (VARCHAR(20))  
- created_at (TIMESTAMPTZ DEFAULT NOW())  
- updated_at (TIMESTAMPTZ DEFAULT NOW())  
- deleted_at (TIMESTAMPTZ)  

### 3.7. Bảng Phần mềm & Bản quyền
**software_installations**  
- id (UUID PRIMARY KEY DEFAULT uuid_generate_v4())  
- device_id (UUID REFERENCES devices(id))  
- software_name (VARCHAR(100))  
- version (VARCHAR(50))  
- publisher (VARCHAR(100))  
- install_date (DATE)  
- license_id (UUID REFERENCES software_licenses(id))  
- is_blocked (BOOLEAN)  
- created_at (TIMESTAMPTZ DEFAULT NOW())  
- updated_at (TIMESTAMPTZ DEFAULT NOW())  
- deleted_at (TIMESTAMPTZ)  

**software_licenses**  
- id (UUID PRIMARY KEY DEFAULT uuid_generate_v4())  
- software_name (VARCHAR(100))  
- license_key_enc (BYTEA)  
- type (VARCHAR(30))  
- total_seats (INTEGER)  
- used_seats (INTEGER DEFAULT 0)  
- purchase_date (DATE)  
- expire_date (DATE)  
- vendor_id (UUID REFERENCES vendors(id))  
- created_at (TIMESTAMPTZ DEFAULT NOW())  
- updated_at (TIMESTAMPTZ DEFAULT NOW())  
- deleted_at (TIMESTAMPTZ)  

**serial_blacklist**  
- id (UUID PRIMARY KEY DEFAULT uuid_generate_v4())  
- serial_number (VARCHAR(100) UNIQUE)  
- reason (TEXT)  
- created_at (TIMESTAMPTZ DEFAULT NOW())  

**software_blacklist**  
- id (UUID PRIMARY KEY DEFAULT uuid_generate_v4())  
- software_name (VARCHAR(100))  
- reason (TEXT)  
- created_at (TIMESTAMPTZ DEFAULT NOW())  

### 3.8. Bảng Vòng đời, Workflow & Audit
**device_assignments**  
- id (UUID PRIMARY KEY DEFAULT uuid_generate_v4())  
- device_id (UUID REFERENCES devices(id))  
- user_id (UUID REFERENCES users(id))  
- assignment_type (VARCHAR(20))  
- assigned_at (TIMESTAMPTZ)  
- returned_at (TIMESTAMPTZ)  
- assigned_by_id (UUID REFERENCES users(id))  
- return_condition (VARCHAR(20))  
- notes (TEXT)  
- created_at (TIMESTAMPTZ DEFAULT NOW())  
- updated_at (TIMESTAMPTZ DEFAULT NOW())  

**notifications**  
- id (UUID PRIMARY KEY DEFAULT uuid_generate_v4())  
- user_id (UUID REFERENCES users(id))  
- title (VARCHAR(200))  
- message (TEXT)  
- type (VARCHAR(20))  
- channel (VARCHAR(20))  
- is_read (BOOLEAN DEFAULT FALSE)  
- related_entity_type (VARCHAR(50))  
- related_entity_id (UUID)  
- created_at (TIMESTAMPTZ DEFAULT NOW())  

**workflow_requests**  
- id (UUID PRIMARY KEY DEFAULT uuid_generate_v4())  
- request_type (VARCHAR(20) NOT NULL)  
- status (VARCHAR(30) DEFAULT 'PENDING_IT')  
- requested_by (UUID REFERENCES users(id))  
- target_user_id (UUID REFERENCES users(id))  
- template_details (JSONB)  
- completed_at (TIMESTAMPTZ)  
- created_at (TIMESTAMPTZ DEFAULT NOW())  
- updated_at (TIMESTAMPTZ DEFAULT NOW())  
- deleted_at (TIMESTAMPTZ)  

**approval_history**  
- id (UUID PRIMARY KEY DEFAULT uuid_generate_v4())  
- entity_type (VARCHAR(50) NOT NULL)  
- entity_id (UUID NOT NULL)  
- action (VARCHAR(20) NOT NULL)  
- user_id (UUID REFERENCES users(id))  
- comment (TEXT)  
- created_at (TIMESTAMPTZ DEFAULT NOW())  

**history_logs**  
- id (UUID DEFAULT uuid_generate_v4())  
- created_at (TIMESTAMPTZ NOT NULL)  
- table_name (VARCHAR(50) NOT NULL)  
- record_id (UUID NOT NULL)  
- action (VARCHAR(20) NOT NULL)  
- old_value (JSONB)  
- new_value (JSONB)  
- changed_by_user_id (UUID REFERENCES users(id))  
- ip_address (INET)  
- user_agent (VARCHAR(255))  
- request_id (UUID NOT NULL)  
- PRIMARY KEY (id, created_at)  
- PARTITION BY RANGE (created_at)  

### 3.9. Cải tiến & Trigger Cấp CSDL (Bắt buộc triển khai)
**1. Xử lý Circular FK cho bảng departments:**  
```sql
ALTER TABLE departments ADD CONSTRAINT fk_dept_manager 
FOREIGN KEY (manager_id) REFERENCES users(id) 
DEFERRABLE INITIALLY DEFERRED;
```

**2. Trigger tự động đồng bộ Used Seats khi Soft Delete License:**  
```sql
CREATE OR REPLACE FUNCTION update_license_seats_on_soft_delete()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.deleted_at IS NOT NULL AND OLD.deleted_at IS NULL THEN
        UPDATE software_licenses SET used_seats = GREATEST(0, used_seats - 1) 
        WHERE id = OLD.license_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_soft_delete_installation
AFTER UPDATE ON software_installations
FOR EACH ROW EXECUTE FUNCTION update_license_seats_on_soft_delete();
```

---

## 4. CHI TIẾT TÍNH NĂNG, LUẬT NGHIỆP VỤ & STATE MACHINES

### Module 1: Thu thập & Định danh thông minh (Inventory Ingestion)
**Endpoint chính:** POST /api/v1/inventory/report  

**Logic phân loại thiết bị:**  
- Máy scan Zebra không dây: Dựa vào bluetooth_mac, dock_serial, model → device_subtype = WIRELESS. Tự động tạo dock và DOCK_PAIRING (hỗ trợ 1 dock ↔ nhiều scanner).  
- Thiết bị COM: Nếu có com_port → device_subtype = COM hoặc HYBRID. Tạo connection_type = "COM".  
- Hybrid USB+COM: Tạo 2 connection riêng biệt.  
- Uninstall license: Backend tìm bản ghi software_installations cũ, đánh dấu soft delete → Trigger DB tự động trừ used_seats. Nếu license_id bị NULL do lỗi cũ, tạo alert cảnh báo. Agent sử dụng inventory_run_id để đảm bảo tính Idempotency (chống gửi trùng lặp do mạng gián đoạn).

### Module 2: Quản lý Linh kiện & Di chuyển
- Linh kiện không S/N: Unique Key = [device_id + component_type + slot_name + hash(specifications)].  
- Tự động di chuyển linh kiện khi Agent báo cáo → cập nhật device_id + ghi history_logs.  
- Phát hiện thiếu linh kiện → tạo alert ngay lập tức.  
- Di chuyển hàng loạt (bulk update location) → Backend ghi 1 log tổng hợp vào history_logs để tránh spam.

### Module 3: Topology Mapping
- Hỗ trợ kết nối NETWORK, POWER, USB, HDMI, COM, WIRELESS_DOCK, DOCK_PAIRING.  
- Blacklist thiết bị tạm (USB, Phone) → is_temporary = True + tự động xóa cứng (hard delete) thiết bị này sau 24h (chỉ giữ lại log trong history_logs).  
- Hiển thị Graph/Tree với React Flow.

### Module 4: Bảo trì, Kho & Bảo hành ngoài
- Sửa chữa ngoài → gắn vendor_id, tạo ticket, cho mượn thiết bị tạm (is_temp_replacement).  
- Vật tư tiêu hao (Consumable) → auto deduct quantity trong spare_parts_inventory + alert khi quantity <= min_quantity.  
- Tracking actual_cost trong tickets và maintenance_logs để đối soát.

### Module 5: Tích hợp RustDesk
- Lưu password bằng AES-256-GCM (Column-level encryption).  
- Ưu tiên nhận Webhook từ RustDesk Server để update trạng thái online; fallback poll Redis Queue interval 1 phút.  
- Password rotation policy: Tự động đổi password sau 90 ngày thông qua background job.

### Module 6: Auth & RBAC
- Hỗ trợ Local (bcrypt/argon2), LDAP/AD, SSO (SAML/OIDC).  
- Ma trận phân quyền chi tiết được thiết kế riêng lẻ, xem chi tiết tại Mục 6 của tài liệu này.

### Module 7: Notification Engine
**12 loại cảnh báo tự động:** Agent offline >7 ngày, Di chuyển linh kiện trái phép, Phần mềm đen/vi phạm bản quyền, Bản quyền sắp hết (30 ngày), Vật tư kho dưới ngưỡng, S/N trùng/clone, Ticket quá SLA, Thu hồi thiết bị failed, Thanh lý chờ duyệt, Bảo hành hết hạn, Reconciliation needed, SLA breach.  

**Kênh:** WebSocket realtime + Email (qua Celery) + tùy chọn tích hợp SMS/Teams Webhook. User có thể tắt/mở từng loại cảnh báo trong cột preferences (JSONB).

### Module 8: Reports & Export
**9 báo cáo chuẩn:** Tổng quan tài sản, Khấu hao tài sản (TCO), Tồn kho hiện tại, Thiết bị Offline/Missing, Chi phí sửa chữa theo tháng, Chi phí mua sắm theo phòng ban, Bản quyền sắp hết hạn, Thống kê Ticket SLA, Top phần mềm được cài nhiều nhất.  

**Xuất file:** Excel (openpyxl), PDF (weasyprint), CSV.  
**Lên lịch:** Celery Beat đọc cấu hình từ DB, gửi tự động vào 01:00 AM ngày 1 hàng tháng.

### Module 9: License Management
- Khi Agent báo cáo software mới → Backend link license_id dựa trên tên phần mềm và cập nhật used_seats.  
- Vi phạm (used_seats > total_seats) → phát sự kiện → auto tạo ticket CRITICAL.  
- Phần mềm đen → so sánh (không phân biệt hoa thường) với bảng software_blacklist → tạo ticket ngay.

### Module 10: Onboarding/Offboarding
- Onboarding: HR tạo request → chọn template → IT approve → tự trừ kho spare_parts, tạo assignment, in QR.  
- Offboarding: HR trigger → tìm tất cả thiết bị qua device_assignments → tạo ticket thu hồi → kiểm tra condition → cập nhật IN_STOCK hoặc DISPOSED + tháo linh kiện trả kho.

### Module 11: Kiểm kê (Physical Inventory)
- Mobile PWA sử dụng IndexedDB (offline-first).  
- Quét Barcode/QR → đánh dấu tick xanh (khớp) / misplaced (sai vị trí) / missing (thất lạc).  
- Khi có mạng, PWA gọi API POST đồng bộ danh sách lên Server.

### STATE MACHINES (Định nghĩa trạng thái bắt buộc)
**Ticket State Machine:**  
- Luồng chuẩn: OPEN → ASSIGNED → IN_PROGRESS → PENDING (chờ vật tư) → RESOLVED → CLOSED.  
- Luồng đặc biệt: Từ bất kỳ trạng thái nào có thể chuyển sang CANCELLED.  
- Luồng hoàn trả: RESOLVED có thể quay lại IN_PROGRESS nếu User xác nhận chưa xong.

**Purchase Order State Machine:**  
- Luồng chuẩn: DRAFT → PENDING_APPROVAL → APPROVED → RECEIVING → COMPLETED.  
- Luồng từ chối: PENDING_APPROVAL → REJECTED (Kết thúc luồng).

**Workflow Request State Machine:**  
- Luồng chuẩn: PENDING_IT → PREPARING → READY_FOR_PICKUP → COMPLETED.

---

## 5. ĐẶC TẢ API, CHUẨN GIAO TIẾP & PROTOCOLS
**Base URL:** /api/v1

### 5.1. Danh sách Endpoints đầy đủ
- **Auth & RBAC:** POST /auth/login, /logout, /refresh, GET /auth/me, POST /auth/ldap-sync, GET/POST/PUT /roles, GET/POST/DELETE /users/{user_id}/roles/{role_id}.  
- **Devices & Components:** GET/POST /devices, GET/PUT/DELETE /devices/{id}, POST /devices/bulk-update-location, GET /devices/{id}/components|connections|software|assignments, POST /devices/{id}/reconcile.  
- **Inventory:** GET/POST /spare-parts, PUT /spare-parts/{id}/adjust, POST /inventory/import|/report.  
- **ITSM & Change:** GET/POST /tickets, GET /tickets/{id}, PATCH /tickets/{id}/status, POST /tickets/{id}/comments|/maintenance-logs, PATCH /tickets/{id}/cab-approve.  
- **Procurement:** GET/POST /purchase-orders, PATCH /purchase-orders/{id}/approve|/reject, POST /purchase-orders/{id}/receive-items.  
- **Vendors & Contracts:** CRUD /vendors, CRUD /contracts.  
- **Workflow:** POST/GET /workflow/requests, PATCH /workflow/requests/{id}/approve|/complete.  
- **License:** GET/POST /licenses, PUT /licenses/{id}, GET /licenses/check-violations.  
- **Reports:** GET /reports/asset-depreciation|/inventory-status|/ticket-sla|/export?format=xlsx|pdf|csv.  
- **Admin & System:** GET/POST /users, GET /departments|/locations|/audit-logs|/notifications, PATCH /notifications/{id}/read, GET/PUT /settings, POST /reconciliation/approve.

### 5.2. Request/Response Body Standards (Ví dụ mẫu)
**POST /api/v1/auth/login**  
**Request:**  
```json
{ 
  "username": "hau.nt", 
  "password": "P@ssw0rd", 
  "provider": "LOCAL" 
}
```  
**Response 200 OK:**  
```json
{ 
  "access_token": "eyJ...", 
  "refresh_token": "eyJ...", 
  "expires_in": 900, 
  "user": { 
    "id": "uuid-cua-hau", 
    "full_name": "Nguyễn Trung Hậu", 
    "roles": ["IT_ADMIN"] 
  } 
}
```

**POST /api/v1/tickets**  
**Request:**  
```json
{ 
  "title": "Máy in bị kẹt giấy", 
  "description": "Tại phòng Kế toán tầng 3", 
  "priority": "MEDIUM", 
  "category": "HARDWARE", 
  "device_id": "uuid-may-in" 
}
```  
**Response 201 Created:**  
```json
{ 
  "id": "uuid-ticket-moi", 
  "ticket_code": "ITSM-2026-00045", 
  "status": "OPEN", 
  "sla_response_due": "2026-03-30T10:15:00Z", 
  "version": 1 
}
```

### 5.3. Error Response Format chuẩn (Theo RFC 7807)
Tất cả lỗi hệ thống phải trả về format sau:  
```json
{
  "type": "https://citms.internal/errors/optimistic-lock-conflict",
  "title": "Xung đột cập nhật dữ liệu",
  "status": 409,
  "detail": "Ticket này đã bị người khác chỉnh sửa trước đó. Vui lòng tải lại trang để xem thay đổi mới nhất.",
  "instance": "/api/v1/tickets/uuid-ticket-moi",
  "trace_id": "X-Request-ID-uuid-gia-tri"
}
```

### 5.4. Pagination & Filtering Strategy
- **Pagination:** Offset-based (?page=1&limit=50) cho bảng nhỏ, Cursor-based cho bảng lớn.  
- **Filtering:** Sử dụng quy tắc OData-like qua Query Params.

### 5.5. Agent Communication Protocol Specification
- **Authentication:** Header `X-Agent-Token: <shared_secret>`.  
- **Idempotency:** Request body bắt buộc có `inventory_run_id` (UUID).  
- **Retry Logic:** Exponential Backoff (1s, 2s, 4s, 8s, tối đa 5 lần).  
- **Rate Limiting:** 50 requests/phút/Agent.

---

## 6. MA TRẬN PHÂN QUYỀN RBAC CHI TIẾT

| Module / Chức năng              | Super Admin | IT Manager     | IT Staff               | HR Staff         | Regular User             |
|--------------------------------|-------------|----------------|------------------------|------------------|--------------------------|
| Quản lý Users/Roles            | Full CRUD   | Read-only      | Read-only              | Read-only        | Chỉ đổi password         |
| Quản lý Thiết bị (Devices)     | Full CRUD   | Full CRUD      | CRUD (không xóa)       | Read-only        | Read-only (của mình)     |
| Xử lý Ticket ITSM              | Toàn quyền  | Full, Re-assign| CRUD (trong queue)     | Tạo mới          | Tạo mới, Read (của mình) |
| Mua sắm (Procurement)          | Duyệt tất cả| Duyệt tất cả   | Read-only              | Tạo yêu cầu      | None                     |
| Quản lý Bản quyền (License)    | Full CRUD   | Full CRUD      | Read-only              | None             | None                     |
| Xem Audit Logs                 | Read All    | Read All       | Read (không IP)        | None             | None                     |
| Cấu hình System Settings       | Full        | Read-only      | None                   | None             | None                     |
| Remote Control (RustDesk)      | Cho phép    | Cho phép       | Cho phép               | Không            | Không                    |
| Reconcile (Xác nhận dữ liệu)   | Phê duyệt   | Phê duyệt      | Đề xuất                | None             | None                     |

---

## 7. ĐỊNH NGHĨA SLA VÀ TICKET ESCALATION RULES

### 7.1. Bảng SLA Cụ thể
SLA được tính tự động dựa trên giờ hành chính (08:00 - 17:00, Thứ 2 - Thứ 6).

| Priority   | Mô tả tình huống                              | Response Time | Resolution Time |
|------------|-----------------------------------------------|---------------|-----------------|
| CRITICAL   | Toàn hệ thống đình trệ, vi phạm bản quyền     | 15 phút       | 4 giờ           |
| HIGH       | Thiết bị Lãnh đạo hoặc phòng trọng yếu hỏng   | 30 phút       | 8 giờ           |
| MEDIUM     | Lỗi ảnh hưởng 1 cá nhân                       | 2 giờ         | 24 giờ          |
| LOW        | Yêu cầu cài đặt mới, consult                  | 8 giờ         | 72 giờ          |

### 7.2. Ticket Escalation Rules (Celery Beat chạy mỗi 5 phút)
- **Time-based Escalation:** Đạt 80% SLA → gửi alert. Quá 100% SLA → chuyển lên IT Manager + đánh dấu SLA_BREACHED.  
- **Inactivity Escalation:** PENDING quá 3 ngày không comment → nhắc User. Quá 7 ngày → tự động RESOLVED.  
- **Priority Bump:** 1 User tạo > 3 ticket HIGH trong 24 giờ → tự động gom thành 1 ticket CRITICAL.

---

## 8. THIẾT KẾ GIAO DIỆN (UI SPECIFICATION)

### 8.1. Dashboard (Tổng hợp)
- Widget 1: Pie Chart tài sản (Đang dùng / Trong kho / Đang sửa / Hỏng).  
- Widget 2: Bar Chart số lượng ticket theo tuần.  
- Widget 3: Agent Health (Online/Offline/Missing).  
- Widget 4: Danh sách cảnh báo quan trọng (list realtime).  
- Widget 5: Timeline các thiết bị hết warranty & license sắp hết hạn.  
- Widget 6: Activity Feed realtime.

### 8.2. Danh sách Thiết bị
- Bảng có filter thông minh (Serial trùng, Clone Conflict, Offline > X ngày, Warranty expiring).  
- Trạng thái RustDesk (đèn xanh/đỏ).

### 8.3. Chi tiết Thiết bị (5 Tabs)
- Tab General: Thông tin cơ bản + Timeline lịch sử cấp phát/thu hồi.  
- Tab Connections: Graph mô phỏng sơ đồ kết nối thực tế bằng React Flow.  
- Tab Software: Danh sách phần mềm + Highlight nền đỏ các phần mềm vi phạm.  
- Tab Components: Bảng linh kiện + Lịch sử luân chuyển.  
- Tab Maintenance: Timeline các lần sửa chữa + Hình ảnh đính kèm.

### 8.4. Các trang khác
- Tickets: Kanban (kéo thả) + Calendar view + tab Change Plan & Rollback.  
- Procurement: Tab “Chờ duyệt” + “Đã duyệt”.  
- License: Progress bar Used/Total realtime.  
- Role Management: CRUD roles và gán role cho user.  
- Workflow Requests: Kanban theo trạng thái.  
- Audit Log: Diff highlight Old → New + filter theo request_id.  
- Settings: Quản lý Blacklist, SMTP, RustDesk, Notification preferences.

---

## 9. YÊU CẦU PHI CHỨC NĂNG (NFR) & BẢO MẬT

### 9.1. Performance & Scalability
- P95 response time < 500ms cho mọi API nội bộ.  
- Hỗ trợ tối thiểu 10.000 Agents gửi report đồng thời.  
- Partitioning cho bảng history_logs theo khoảng thời gian.  
- Cache Redis thời gian 5-15 phút cho các truy vấn Dashboard nặng.

### 9.2. Reliability & Backup
- Full backup lúc 01:00 AM hàng ngày + WAL incremental mỗi 15 phút.  
- RTO < 4 giờ, RPO < 6 giờ.  
- Backup tự động đẩy lên S3 khác region.

### 9.3. Observability
- Toàn bộ log hệ thống viết theo chuẩn Structured JSON.  
- Mọi log phải chứa request_id.  
- Tích hợp Sentry, Prometheus, Grafana.

### 9.4. Password & Security Policy
- Độ mạnh mật khẩu: Tối thiểu 12 ký tự, có chữ hoa, thường, số, ký tự đặc biệt. Không trùng 5 mật khẩu gần nhất.  
- Khóa tài khoản: Sai 5 lần → khóa 15 phút.  
- Session: Idle timeout 30 phút.  
- Mã hóa: AES-256-GCM cho trường nhạy cảm.  
- Network: HTTPS TLS 1.2+ bắt buộc, Anti-CSRF, XSS protection, CORS strict.

### 9.5. Data Retention Policy
- Dữ liệu cốt lõi: Lưu vĩnh viễn (Soft Delete).  
- History Logs: Tự động xóa partition cũ hơn 3 năm.  
- Notifications: Xóa cứng thông báo đã đọc cũ hơn 6 tháng.  
- Thiết bị tạm: Xóa cứng sau 24h.

---

## 10. CHIẾN LƯỢC DATA MIGRATION (CHUYỂN ĐỔI DỮ LIỆU CŨ)
Hệ thống cũ (GLPI/Excel) cần được chuyển đổi sang CITMS mới mà không làm gián đoạn hoạt động của công ty. Quy trình thực hiện như sau:  
- **Phase 1 - Extract & Cleanse (Trích xuất và Làm sạch):** Dump dữ liệu thô từ Database cũ. Viết Script Python tự động chuẩn hóa dữ liệu: Loại bỏ khoảng trắng dư thừa, chuyển toàn bộ Serial Number sang dạng UPPERCASE. Loại bỏ các record bị trùng lặp dựa trên tổ hợp khóa `serial_number` và `primary_mac`.  
- **Phase 2 - Transform (Chuyển đổi cấu trúc):** Map ID cũ (thường là INT AUTO_INCREMENT) sang UUID v4 mới của CITMS. Bắt buộc xây dựng 1 bảng mapping tạm thời trong database (`old_int_id` -> `new_uuid`) để đảm bảo không đứt gãy các quan hệ Foreign Key.  
- **Phase 3 - Load & Parallel Run (Tải lên và Chạy song song):** Inject dữ liệu đã transform vào DB CITMS. Đặt tất cả thiết bị được migrate ở trạng thái `IN_USE`. Cấu hình lại GLPI Agent bản mới để gửi dữ liệu song song về cả hệ thống cũ và CITMS trong vòng 1 tuần.  
- **Phase 4 - Validation & Cutover (Kiểm chứng và Chuyển đổi):** Mỗi ngày chạy job tự động so sánh số lượng Asset, số lượng Ticket giữa hệ thống cũ và CITMS. Nếu dữ liệu khớp 100% trong 3 ngày liên tục → thực hiện Switch DNS/VIP để User truy cập vào CITMS.  
- **Rollback Plan:** Giữ Database cũ chạy ở chế độ Read-only tối thiểu 30 ngày sau khi chuyển đổi. Nếu phát hiện lỗi nghiêm trọng trên CITMS, lập tức chuyển DNS về hệ thống cũ.

---

## 11. KIẾN TRÚC DEPLOYMENT & CI/CD
### 11.1. Môi trường
Hệ thống được triển khai trên 3 môi trường tách biệt hoàn toàn về mặt dữ liệu: `Dev` (Phát triển nội bộ) → `Staging` (Kiểm thử UAT bởi Business) → `Production` (On-premise).

### 11.2. CI Pipeline (Tích hợp liên tục)
Sử dụng GitLab CI hoặc Jenkins. Pipeline sẽ tự động trigger khi có Merge Request vào nhánh `main` hoặc `develop`:  
- **Bước 1 (Lint):** Chạy Ruff kiểm tra chuẩn code Python và ESLint cho React.  
- **Bước 2 (Test):** Chạy Unit Tests & Integration Tests (Pytest). Bắt buộc đạt Coverage **≥ 80%** mới được pass.  
- **Bước 3 (Build):** Build Docker Image (`docker build -t registry.internal/citms-api:v3.0.x`).  
- **Bước 4 (Push):** Push Image lên Private Docker Registry nội bộ của công ty.

### 11.3. CD Pipeline (Triển khai liên tục)
- **Staging:** Tự động deploy qua Docker Compose khi code được merge thành công.  
- **Production:** Yêu cầu Manual Approval (Tech Lead bấm nút xác nhận trên GitLab/Jenkins).  
- **Chiến thuật:** Sử dụng **Blue-Green Deployment** thông qua Docker Swarm hoặc K3s để đảm bảo thời gian downtime bằng 0 khi cập nhật phiên bản mới, đáp ứng mục tiêu RTO < 4 giờ.

### 11.4. Infrastructure as Code (IaC)
Toàn bộ quá trình cài đặt OS, cấu hình Network, cài đặt Docker, PostgreSQL, Redis, MinIO, tường lửa (UFW) phải được viết bằng **Ansible Playbook**. Điều này đảm bảo việc init môi trường mới diễn ra chính xác, đồng nhất và nhanh chóng dưới 30 phút.

---

## 12. YÊU CẦU KIỂM THỬ (Testing Requirements)
- Unit & Integration Tests ≥ 80% coverage.  
- E2E Tests cho tất cả 12 luồng chính.  
- Load Tests cho 10.000 Agents.  
- Security & Penetration Tests trước Production.