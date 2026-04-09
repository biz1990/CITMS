"""setup pg_cron mv refresh

Revision ID: 20260409_cron
Revises: 20260409_remediation
Create Date: 2026-04-09 10:55:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20260409_cron'
down_revision = '20260409_remediation'
branch_labels = None
depends_on = None

def upgrade():
    # 1. Enable pg_cron extension (requires superuser)
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_cron")
    
    # 2. Create Refresh Function
    op.execute("""
        CREATE OR REPLACE FUNCTION refresh_matview_inventory()
        RETURNS void LANGUAGE plpgsql AS $$
        BEGIN
            REFRESH MATERIALIZED VIEW CONCURRENTLY mv_inventory_summary;
        END;
        $$;
    """)
    
    # 3. Schedule Cron Job (Every 15 minutes)
    # Note: 'cron.job' is the table where pg_cron stores jobs
    op.execute("""
        SELECT cron.schedule('inventory-mv-refresh', '*/15 * * * *', 'SELECT refresh_matview_inventory()');
    """)

def downgrade():
    op.execute("SELECT cron.unschedule('inventory-mv-refresh')")
    op.execute("DROP FUNCTION IF EXISTS refresh_matview_inventory()")
