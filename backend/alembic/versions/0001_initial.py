"""initial schema

Revision ID: 0001
Revises: 
Create Date: 2026-03-31 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # -------------------------------------------------------------
    # Note: Lệnh `alembic revision --autogenerate` sẽ tự thiết lập
    # toàn bộ `op.create_table` dựa trên cấu trúc `Base.metadata`.
    # Dưới đây là các phần mở rộng CUSTOM DDL (Yêu cầu khắt khe từ SRS)
    # bạn cần gộp vào khi hoàn thành auto generate.
    # -------------------------------------------------------------

    # 1. Bổ sung extension sinh UUID v4 cho Postgres
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')

    # 2. Xử lý Circular FK cho bảng departments (manager_id deferrable)
    # Cần chắc chắn lệnh này chạy sau khi bảng departments và users đã được tạo.
    op.execute('''
        ALTER TABLE departments ADD CONSTRAINT fk_dept_manager 
        FOREIGN KEY (manager_id) REFERENCES users(id) 
        DEFERRABLE INITIALLY DEFERRED;
    ''')

    # 3. Trigger tự động đồng bộ Used Seats khi Soft Delete License Installation
    op.execute('''
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
    ''')
    op.execute('''
        CREATE TRIGGER trg_soft_delete_installation
        AFTER UPDATE ON software_installations
        FOR EACH ROW EXECUTE FUNCTION update_license_seats_on_soft_delete();
    ''')

    # 4. Tạo bảng History Logs với Time-Partitioning
    # Chú ý: Cần tắt generate bảng này cho alembic nếu đã có Models tương ứng
    # do ORM ko tự sinh `PARTITION BY RANGE`
    op.execute('''
        CREATE TABLE IF NOT EXISTS history_logs (
            id UUID DEFAULT uuid_generate_v4(),
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            table_name VARCHAR(50) NOT NULL,
            record_id UUID NOT NULL,
            action VARCHAR(20) NOT NULL,
            old_value JSONB,
            new_value JSONB,
            changed_by_user_id UUID REFERENCES users(id),
            ip_address INET,
            user_agent VARCHAR(255),
            request_id UUID NOT NULL,
            PRIMARY KEY (id, created_at)
        ) PARTITION BY RANGE (created_at);
        
        -- Default partition cho dữ liệu năm hiện hành
        CREATE TABLE IF NOT EXISTS history_logs_2026 
        PARTITION OF history_logs FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');
    ''')


def downgrade() -> None:
    # Revert các Custom SQL
    op.execute('DROP TABLE IF EXISTS history_logs CASCADE;')
    op.execute('DROP TRIGGER IF EXISTS trg_soft_delete_installation ON software_installations;')
    op.execute('DROP FUNCTION IF EXISTS update_license_seats_on_soft_delete();')
    op.execute('ALTER TABLE departments DROP CONSTRAINT IF EXISTS fk_dept_manager;')
    
    # -------------------------------------------------------------
    # Auto-generated op.drop_table() sẽ được alembic đặt phía dưới
    # -------------------------------------------------------------
