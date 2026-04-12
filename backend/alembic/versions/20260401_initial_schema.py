"""Initial schema - CITMS v3.6

Revision ID: 20260401_initial_schema
Revises: 
Create Date: 2026-04-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20260401_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Enable extensions
    op.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    # --- Core Tables (no dependencies) ---

    op.create_table(
        'departments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('version', sa.Integer(), server_default='1', nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('code', sa.String(20), unique=True, nullable=True),
        sa.Column('manager_id', postgresql.UUID(as_uuid=True), nullable=True),
    )

    op.create_table(
        'locations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('version', sa.Integer(), server_default='1', nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('city', sa.String(100), nullable=True),
        sa.Column('country', sa.String(100), nullable=True),
    )

    op.create_table(
        'roles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('version', sa.Integer(), server_default='1', nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
    )

    op.create_table(
        'permissions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('version', sa.Integer(), server_default='1', nullable=False),
        sa.Column('name', sa.String(100), nullable=False, unique=True),
        sa.Column('resource', sa.String(50), nullable=False),
        sa.Column('action', sa.String(50), nullable=False),
    )

    op.create_table(
        'vendors',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('version', sa.Integer(), server_default='1', nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('contact_email', sa.String(255), nullable=True),
        sa.Column('contact_phone', sa.String(50), nullable=True),
        sa.Column('website', sa.String(500), nullable=True),
        sa.Column('tax_id', sa.String(50), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('country', sa.String(100), nullable=True),
    )

    # --- Users (depends on departments, locations) ---

    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('version', sa.Integer(), server_default='1', nullable=False),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('username', sa.String(100), nullable=False, unique=True),
        sa.Column('full_name', sa.String(200), nullable=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('is_superuser', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('department_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('departments.id'), nullable=True),
        sa.Column('location_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('locations.id'), nullable=True),
        sa.Column('refresh_token', sa.Text(), nullable=True),
        sa.Column('password_changed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('failed_login_attempts', sa.Integer(), server_default='0', nullable=False),
        sa.Column('locked_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('mfa_secret', sa.String(200), nullable=True),
        sa.Column('mfa_enabled', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('avatar_url', sa.String(500), nullable=True),
        sa.Column('language_preference', sa.String(10), server_default='vi', nullable=True),
    )

    op.create_foreign_key(
        'departments_manager_id_fkey', 'departments', 'users',
        ['manager_id'], ['id'], deferrable=True, initially='DEFERRED'
    )

    op.create_table(
        'role_permissions',
        sa.Column('role_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('roles.id'), primary_key=True),
        sa.Column('permission_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('permissions.id'), primary_key=True),
    )

    op.create_table(
        'user_roles',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), primary_key=True),
        sa.Column('role_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('roles.id'), primary_key=True),
    )

    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('version', sa.Integer(), server_default='1', nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('resource_type', sa.String(50), nullable=False),
        sa.Column('resource_id', sa.String(100), nullable=True),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('details', postgresql.JSONB(), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
    )

    # --- Asset Tables ---

    op.create_table(
        'devices',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('version', sa.Integer(), server_default='1', nullable=False),
        sa.Column('hostname', sa.String(100), nullable=False),
        sa.Column('serial_number', sa.String(100), nullable=True),
        sa.Column('asset_tag', sa.String(50), nullable=True),
        sa.Column('device_type', sa.String(30), nullable=False),
        sa.Column('status', sa.String(30), server_default='ACTIVE', nullable=False),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('mac_address', sa.String(17), nullable=True),
        sa.Column('bluetooth_mac', sa.String(17), nullable=True),
        sa.Column('os_type', sa.String(30), nullable=True),
        sa.Column('os_version', sa.String(100), nullable=True),
        sa.Column('manufacturer', sa.String(100), nullable=True),
        sa.Column('model', sa.String(100), nullable=True),
        sa.Column('cpu', sa.String(200), nullable=True),
        sa.Column('ram_gb', sa.Integer(), nullable=True),
        sa.Column('storage_gb', sa.Integer(), nullable=True),
        sa.Column('purchase_date', sa.Date(), nullable=True),
        sa.Column('purchase_price', sa.Float(), nullable=True),
        sa.Column('depreciation_years', sa.Integer(), nullable=True),
        sa.Column('salvage_value', sa.Float(), nullable=True),
        sa.Column('warranty_expiry', sa.Date(), nullable=True),
        sa.Column('last_seen', sa.DateTime(timezone=True), nullable=True),
        sa.Column('agent_version', sa.String(50), nullable=True),
        sa.Column('rustdesk_id', sa.String(100), nullable=True),
        sa.Column('location_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('locations.id'), nullable=True),
        sa.Column('department_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('departments.id'), nullable=True),
        sa.Column('assigned_to_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('vendor_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('vendors.id'), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('qr_code_token', sa.String(100), nullable=True),
    )

    op.create_table(
        'device_components',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('version', sa.Integer(), server_default='1', nullable=False),
        sa.Column('device_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('devices.id'), nullable=False),
        sa.Column('component_type', sa.String(50), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('serial_number', sa.String(100), nullable=True),
        sa.Column('specifications', postgresql.JSONB(), nullable=True),
    )

    op.create_table(
        'device_connections',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('version', sa.Integer(), server_default='1', nullable=False),
        sa.Column('source_device_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('devices.id'), nullable=False),
        sa.Column('target_device_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('devices.id'), nullable=False),
        sa.Column('connection_type', sa.String(50), nullable=False),
        sa.Column('port', sa.String(20), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
    )

    # --- Software / License Tables ---

    op.create_table(
        'software_catalog',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('version', sa.Integer(), server_default='1', nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('publisher', sa.String(100), nullable=True),
        sa.Column('regex_pattern', sa.String(255), nullable=True),
    )

    op.create_table(
        'software_licenses',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('version', sa.Integer(), server_default='1', nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('license_key', sa.Text(), nullable=True),
        sa.Column('software_name', sa.String(200), nullable=False),
        sa.Column('vendor_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('vendors.id'), nullable=True),
        sa.Column('license_type', sa.String(50), nullable=True),
        sa.Column('total_seats', sa.Integer(), nullable=False),
        sa.Column('used_seats', sa.Integer(), server_default='0', nullable=False),
        sa.Column('expiry_date', sa.Date(), nullable=True),
        sa.Column('purchase_date', sa.Date(), nullable=True),
        sa.Column('purchase_price', sa.Float(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
    )

    op.create_table(
        'software_installations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        # NOTE: 'version' column from base model is the row version counter.
        # Software version string is handled by the model's 'version' field which shadows the base.
        # We use sw_version here to avoid conflict - the model handles it as 'version' column
        sa.Column('version', sa.String(50), nullable=True),
        sa.Column('device_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('devices.id'), nullable=False),
        sa.Column('software_catalog_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('software_catalog.id'), nullable=True),
        sa.Column('license_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('software_licenses.id'), nullable=True),
        sa.Column('install_date', sa.DateTime(), nullable=True),
        sa.Column('is_blocked', sa.Boolean(), server_default='false', nullable=False),
    )

    op.create_table(
        'software_blacklist',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('version', sa.Integer(), server_default='1', nullable=False),
        sa.Column('software_name_pattern', sa.String(200), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('added_by_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
    )

    op.create_table(
        'serial_blacklist',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('version', sa.Integer(), server_default='1', nullable=False),
        sa.Column('serial_number', sa.String(100), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('added_by_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
    )

    op.create_table(
        'inventory_run_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('inventory_run_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('device_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('devices.id'), nullable=True),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('error_message', sa.String(), nullable=True),
        sa.Column('processing_time_ms', sa.Integer(), nullable=True),
    )

    op.create_table(
        'reconciliation_conflicts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('version', sa.Integer(), server_default='1', nullable=False),
        sa.Column('device_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('devices.id'), nullable=False),
        sa.Column('field_name', sa.String(50), nullable=False),
        sa.Column('agent_value', sa.String(), nullable=True),
        sa.Column('manual_value', sa.String(), nullable=True),
        sa.Column('agent_reported_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('server_updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(20), server_default='PENDING', nullable=False),
        sa.Column('resolution_choice', sa.String(20), nullable=True),
    )

    # --- ITSM Tables ---

    op.create_table(
        'tickets',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('version', sa.Integer(), server_default='1', nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(30), server_default='OPEN', nullable=False),
        sa.Column('priority', sa.String(20), server_default='MEDIUM', nullable=False),
        sa.Column('category', sa.String(50), nullable=True),
        sa.Column('reporter_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('assignee_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('department_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('departments.id'), nullable=True),
        sa.Column('location_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('locations.id'), nullable=True),
        sa.Column('device_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('devices.id'), nullable=True),
        sa.Column('vendor_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('vendors.id'), nullable=True),
        sa.Column('sla_deadline', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_sla_breached', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('closed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_change_request', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('change_plan', sa.Text(), nullable=True),
        sa.Column('rollback_plan', sa.Text(), nullable=True),
        sa.Column('cab_approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cab_approver_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
    )

    op.create_table(
        'ticket_comments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('version', sa.Integer(), server_default='1', nullable=False),
        sa.Column('ticket_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tickets.id'), nullable=False),
        sa.Column('author_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('is_internal', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('attachments', postgresql.JSONB(), nullable=True),
    )

    op.create_table(
        'maintenance_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('version', sa.Integer(), server_default='1', nullable=False),
        sa.Column('device_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('devices.id'), nullable=False),
        sa.Column('ticket_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tickets.id'), nullable=True),
        sa.Column('technician_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('action_taken', sa.Text(), nullable=False),
        sa.Column('spare_parts_used', postgresql.JSONB(), nullable=True),
        sa.Column('cost', sa.Integer(), server_default='0', nullable=False),
        sa.Column('maintenance_date', sa.DateTime(), nullable=True),
    )

    op.create_table(
        'system_holidays',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('version', sa.Integer(), server_default='1', nullable=False),
        sa.Column('holiday_date', sa.DateTime(), nullable=False, unique=True),
        sa.Column('description', sa.String(200), nullable=False),
    )

    # --- Procurement Tables ---

    op.create_table(
        'contracts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('version', sa.Integer(), server_default='1', nullable=False),
        sa.Column('contract_number', sa.String(100), nullable=False, unique=True),
        sa.Column('vendor_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('vendors.id'), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('value', sa.Float(), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(30), server_default='ACTIVE', nullable=False),
        sa.Column('document_url', sa.String(500), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
    )

    op.create_table(
        'purchase_orders',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('version', sa.Integer(), server_default='1', nullable=False),
        sa.Column('po_number', sa.String(100), nullable=False, unique=True),
        sa.Column('vendor_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('vendors.id'), nullable=False),
        sa.Column('contract_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('contracts.id'), nullable=True),
        sa.Column('requester_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('approver_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('status', sa.String(30), server_default='DRAFT', nullable=False),
        sa.Column('total_amount', sa.Float(), nullable=True),
        sa.Column('order_date', sa.Date(), nullable=True),
        sa.Column('delivery_date', sa.Date(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
    )

    op.create_table(
        'purchase_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('version', sa.Integer(), server_default='1', nullable=False),
        sa.Column('po_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('purchase_orders.id'), nullable=False),
        sa.Column('description', sa.String(500), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('unit_price', sa.Float(), nullable=False),
        sa.Column('device_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('devices.id'), nullable=True),
    )

    # --- Workflow Tables ---

    op.create_table(
        'workflow_requests',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('version', sa.Integer(), server_default='1', nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('type', sa.String(30), nullable=False),
        sa.Column('status', sa.String(30), server_default='PENDING_IT', nullable=False),
        sa.Column('requested_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('effective_date', sa.DateTime(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
    )

    op.create_table(
        'device_assignments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('version', sa.Integer(), server_default='1', nullable=False),
        sa.Column('device_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('devices.id'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('assigned_at', sa.DateTime(), nullable=True),
        sa.Column('returned_at', sa.DateTime(), nullable=True),
        sa.Column('condition_on_assign', sa.String(), nullable=True),
        sa.Column('condition_on_return', sa.String(), nullable=True),
        sa.Column('qr_code_token', sa.String(100), nullable=True),
    )

    op.create_table(
        'approval_history',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('version', sa.Integer(), server_default='1', nullable=False),
        sa.Column('request_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('workflow_requests.id'), nullable=False),
        sa.Column('approver_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('comments', sa.Text(), nullable=True),
        sa.Column('step_name', sa.String(50), nullable=True),
    )

    # --- Notification Tables ---

    op.create_table(
        'notifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('version', sa.Integer(), server_default='1', nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('is_read', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('resource_type', sa.String(50), nullable=True),
        sa.Column('resource_id', sa.String(100), nullable=True),
        sa.Column('priority', sa.String(20), server_default='NORMAL', nullable=False),
    )

    op.create_table(
        'notification_preferences',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('version', sa.Integer(), server_default='1', nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False, unique=True),
        sa.Column('email_enabled', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('push_enabled', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('types_subscribed', postgresql.JSONB(), nullable=True),
    )

    # --- System Settings ---

    op.create_table(
        'system_settings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('version', sa.Integer(), server_default='1', nullable=False),
        sa.Column('key', sa.String(100), nullable=False, unique=True),
        sa.Column('value', sa.Text(), nullable=True),
        sa.Column('description', sa.String(500), nullable=True),
    )

    # GIN index for audit_logs details
    op.execute("CREATE INDEX idx_audit_logs_details_gin ON audit_logs USING GIN (details)")


def downgrade():
    op.drop_table('system_settings')
    op.drop_table('notification_preferences')
    op.drop_table('notifications')
    op.drop_table('approval_history')
    op.drop_table('device_assignments')
    op.drop_table('workflow_requests')
    op.drop_table('purchase_items')
    op.drop_table('purchase_orders')
    op.drop_table('contracts')
    op.drop_table('system_holidays')
    op.drop_table('maintenance_logs')
    op.drop_table('ticket_comments')
    op.drop_table('tickets')
    op.drop_table('reconciliation_conflicts')
    op.drop_table('inventory_run_logs')
    op.drop_table('serial_blacklist')
    op.drop_table('software_blacklist')
    op.drop_table('software_installations')
    op.drop_table('software_licenses')
    op.drop_table('software_catalog')
    op.drop_table('device_connections')
    op.drop_table('device_components')
    op.drop_table('devices')
    op.drop_table('vendors')
    op.drop_table('audit_logs')
    op.drop_table('user_roles')
    op.drop_table('role_permissions')
    op.drop_constraint('departments_manager_id_fkey', 'departments', type_='foreignkey')
    op.drop_table('users')
    op.drop_table('permissions')
    op.drop_table('roles')
    op.drop_table('locations')
    op.drop_table('departments')
