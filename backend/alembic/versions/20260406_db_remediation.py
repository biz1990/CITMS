"""Database Remediation v3.6.2

Revision ID: 20260406_db_remediation
Revises: 
Create Date: 2026-04-06 05:43:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision = '20260406_db_remediation'
down_revision = '20260401_initial_schema'
branch_labels = None
depends_on = None

def upgrade():
    # 1. Partial Unique Indexes for Devices
    op.create_index(
        'idx_device_serial_unique', 
        'devices', 
        ['serial_number'], 
        unique=True, 
        postgresql_where=text("deleted_at IS NULL")
    )
    op.create_index(
        'idx_device_hostname_unique', 
        'devices', 
        ['hostname'], 
        unique=True, 
        postgresql_where=text("deleted_at IS NULL")
    )

    # 2. Check Constraints for Software Licenses
    op.create_check_constraint(
        'check_used_seats_non_negative',
        'software_licenses',
        'used_seats >= 0'
    )
    op.create_check_constraint(
        'check_total_seats_positive',
        'software_licenses',
        'total_seats > 0'
    )

def downgrade():
    # 1. Remove Check Constraints
    op.drop_constraint('check_used_seats_non_negative', 'software_licenses', type_='check')
    op.drop_constraint('check_total_seats_positive', 'software_licenses', type_='check')

    # 2. Remove Partial Unique Indexes
    op.drop_index('idx_device_serial_unique', table_name='devices')
    op.drop_index('idx_device_hostname_unique', table_name='devices')
