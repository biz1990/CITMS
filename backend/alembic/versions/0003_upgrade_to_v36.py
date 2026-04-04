"""upgrade CITMS to v3.6 enterprise resilient

Revision ID: 0003
Revises: 0002
Create Date: 2026-04-04 14:42:00.000000

Purpose:
    Implementation of Phase 1 Database Schema expansion for CITMS v3.6.
    Includes:
    - Granular Permissions & Role-Permission mapping (v3.6 §3.1)
    - Software Catalog with Regex mapping (v3.6 §4.1)
    - HMAC Agent Identification & last_reconciled_at (v3.6 §1.4, §4.1)
    - Extended Optimistic Locking (v3.6 §1.4)
    - Pessimistic Locking logic via Trigger + Advisory Locks (v3.6 §9.4)
    - Materialized Views for Enterprise Reporting (v3.6 §3.11)
"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0003'
down_revision: Union[str, None] = '0002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- 1. New Tables for RBAC & Software Mapping ---
    
    # Permissions Table (v3.6 §3.1)
    op.create_table(
        'permissions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('code', sa.String(length=100), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )

    # Role-Permission Mapping (v3.6 §3.1)
    op.create_table(
        'role_permissions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('role_id', sa.UUID(), nullable=False),
        sa.Column('permission_id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('role_id', 'permission_id', name='uq_role_permission')
    )

    # Software Catalog Table (v3.6 §4.1)
    op.create_table(
        'software_catalog',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('regex_pattern', sa.String(length=255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # CMDB Relationships (v3.6 §3.3)
    op.create_table(
        'cmdb_relationships',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('source_id', sa.UUID(), nullable=False),
        sa.Column('target_id', sa.UUID(), nullable=False),
        sa.Column('relationship_type', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint('source_id != target_id', name='chk_no_self_relation'),
        sa.ForeignKeyConstraint(['source_id'], ['devices.id'], ),
        sa.ForeignKeyConstraint(['target_id'], ['devices.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # --- 2. Column Modifications (v3.6 §1.4, §4.1) ---

    # Devices updates
    op.add_column('devices', sa.Column('agent_token_hash', sa.String(length=255), nullable=True))
    op.add_column('devices', sa.Column('last_reconciled_at', sa.DateTime(timezone=True), nullable=True))
    # Note: rustdesk_password_enc is NOT dropped due to v3.6 §11.4 "No-Drop" rule. 
    # It remains deprecated in code logic.

    # Optimistic Locking Version columns
    op.add_column('workflow_requests', sa.Column('version', sa.Integer(), server_default='1', nullable=False))
    # PurchaseOrder already has it in v3.0 check.

    # --- 3. Pessimistic Locking Trigger (v3.6 §9.4) ---
    op.execute(sa.text("""
        CREATE OR REPLACE FUNCTION manage_license_seats_v36()
        RETURNS TRIGGER AS $$
        BEGIN
            -- v3.6 Pessimistic Locking via Advisory Lock on license_id
            -- prevents race conditions on used_seats during high-volume ingestion
            IF (TG_OP = 'INSERT') THEN
                IF NEW.license_id IS NOT NULL THEN
                    PERFORM pg_advisory_xact_lock(hashtext(NEW.license_id::text));
                    UPDATE software_licenses 
                    SET used_seats = used_seats + 1 
                    WHERE id = NEW.license_id;
                END IF;
            ELSIF (TG_OP = 'UPDATE') THEN
                -- Handle moving software between devices or changing license
                IF (OLD.license_id IS NOT NULL AND OLD.deleted_at IS NULL AND (NEW.deleted_at IS NOT NULL OR NEW.license_id != OLD.license_id)) THEN
                    PERFORM pg_advisory_xact_lock(hashtext(OLD.license_id::text));
                    UPDATE software_licenses SET used_seats = used_seats - 1 WHERE id = OLD.license_id;
                END IF;
                IF (NEW.license_id IS NOT NULL AND NEW.deleted_at IS NULL AND (OLD.deleted_at IS NOT NULL OR NEW.license_id != OLD.license_id)) THEN
                    PERFORM pg_advisory_xact_lock(hashtext(NEW.license_id::text));
                    UPDATE software_licenses SET used_seats = used_seats + 1 WHERE id = NEW.license_id;
                END IF;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """))

    op.execute(sa.text("""
        DROP TRIGGER IF EXISTS trigger_manage_license_seats ON software_installations;
        CREATE TRIGGER trigger_manage_license_seats
        AFTER INSERT OR UPDATE ON software_installations
        FOR EACH ROW EXECUTE FUNCTION manage_license_seats_v36();
    """))

    # --- 4. Materialized Views for Reporting (v3.6 §3.11, §9.1) ---
    
    # MV: Asset Depreciation (v3.6 §3.11)
    op.execute(sa.text("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS mv_asset_depreciation AS
        SELECT 
            id, asset_tag, name, manufacturer, model, purchase_date, purchase_cost,
            CASE 
                WHEN depreciation_method = 'STRAIGHT_LINE' THEN 
                    GREATEST(0, purchase_cost - (EXTRACT(YEAR FROM age(now(), purchase_date)) * (purchase_cost / 5)))
                ELSE purchase_cost
            END as current_value
        FROM devices
        WHERE deleted_at IS NULL;
    """))
    op.execute(sa.text("CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_depreciation_id ON mv_asset_depreciation (id);"))

    # MV: Software Usage Top 10 (v3.6 §3.11)
    op.execute(sa.text("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS mv_software_usage_top10 AS
        SELECT 
            software_name, COUNT(*) as install_count
        FROM software_installations
        WHERE deleted_at IS NULL
        GROUP BY software_name
        ORDER BY install_count DESC
        LIMIT 10;
    """))
    op.execute(sa.text("CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_sw_usage_name ON mv_software_usage_top10 (software_name);"))

    # MV: Ticket SLA Stats (v3.6 §3.11)
    op.execute(sa.text("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS mv_ticket_sla_stats AS
        SELECT 
            status, is_sla_breached, COUNT(*) as ticket_count
        FROM tickets
        GROUP BY status, is_sla_breached;
    """))
    op.execute(sa.text("CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_sla_stats ON mv_ticket_sla_stats (status, is_sla_breached);"))

    # MV: Offline/Missing Devices (v3.6 §3.11)
    op.execute(sa.text("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS mv_offline_missing_devices AS
        SELECT 
            id, name, asset_tag, last_seen,
            EXTRACT(DAY FROM (now() - last_seen)) as days_offline
        FROM devices
        WHERE last_seen < (now() - INTERVAL '7 days') AND deleted_at IS NULL;
    """))
    op.execute(sa.text("CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_offline_id ON mv_offline_missing_devices (id);"))


def downgrade() -> None:
    # Note: Downgrade is optional and risky for partitioned data/views.
    # We follow §11.4 strictly but provide basic rollback logic for new entities.
    op.execute(sa.text("DROP MATERIALIZED VIEW IF EXISTS mv_offline_missing_devices;"))
    op.execute(sa.text("DROP MATERIALIZED VIEW IF EXISTS mv_ticket_sla_stats;"))
    op.execute(sa.text("DROP MATERIALIZED VIEW IF EXISTS mv_software_usage_top10;"))
    op.execute(sa.text("DROP MATERIALIZED VIEW IF EXISTS mv_asset_depreciation;"))
    
    op.drop_column('workflow_requests', 'version')
    op.drop_column('devices', 'last_reconciled_at')
    op.drop_column('devices', 'agent_token_hash')
    
    op.drop_table('cmdb_relationships')
    op.drop_table('software_catalog')
    op.drop_table('role_permissions')
    op.drop_table('permissions')
