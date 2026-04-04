"""add indexes for Module 8 Reports performance

Revision ID: 0002
Revises: 0001
Create Date: 2026-04-02 07:34:00.000000

Purpose:
    Performance optimization indexes for Module 8 (Reports & Export).
    All indexes use CONCURRENTLY to avoid table locks in production.

    IMPORTANT – Alembic & CONCURRENTLY:
    CREATE INDEX CONCURRENTLY cannot run inside a transaction block.
    We work around this by temporarily switching the connection to
    AUTOCOMMIT mode before each CONCURRENTLY statement, then restoring
    the default isolation level afterward.  Each index is therefore an
    independent DDL operation (no implicit rollback if a later one fails –
    that is acceptable because every statement is idempotent via IF NOT EXISTS).

Indexes created (8 total):
    device_components     → idx_dc_type_deleted          B-tree  (component_type, deleted_at)
    device_components     → idx_dc_device_type           B-tree  (device_id, component_type)
    device_components     → idx_dc_specifications_gin    GIN     specifications JSONB
    software_installations→ idx_si_device_deleted        B-tree  (device_id, deleted_at)
    software_installations→ idx_si_software_name         B-tree  (software_name)
    software_installations→ idx_si_license_id            B-tree  (license_id)
    software_installations→ idx_si_software_name_trgm   GIN/trgm software_name  (pg_trgm)
    devices               → idx_devices_assigned_deleted B-tree  (assigned_to_id, deleted_at)
"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import text

# ---------------------------------------------------------------------------
# Revision identifiers
# ---------------------------------------------------------------------------
revision: str = '0002'
down_revision: Union[str, None] = '0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# ---------------------------------------------------------------------------
# Helper: run one DDL statement in AUTOCOMMIT so CONCURRENTLY works
# ---------------------------------------------------------------------------
def _run_autocommit(sql: str) -> None:
    """Execute *sql* outside any transaction block (required for CONCURRENTLY)."""
    bind = op.get_bind()
    # Execution in autocommit: the connection-level option propagates only to
    # this execution call; the enclosing Alembic transaction is NOT affected.
    bind.execution_options(isolation_level="AUTOCOMMIT").execute(text(sql))


# ---------------------------------------------------------------------------
# upgrade
# ---------------------------------------------------------------------------
def upgrade() -> None:

    # ── 0. Extensions ───────────────────────────────────────────────────────
    # pg_trgm: required for GIN trigram index on software_name (ILIKE support)
    op.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm;"))
    # uuid-ossp: already in 0001, but safe to repeat with IF NOT EXISTS
    op.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'))

    # ── 1. device_components : idx_dc_type_deleted ──────────────────────────
    # Used by: RAM Inventory (Q1), Component Summary (Q3)
    # Rationale: nearly every report query filters WHERE component_type = 'RAM'
    #            AND deleted_at IS NULL.  Composite B-tree eliminates both
    #            conditions in a single index scan.
    _run_autocommit("""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_dc_type_deleted
        ON device_components (component_type, deleted_at);
    """)

    # ── 2. device_components : idx_dc_device_type ───────────────────────────
    # Used by: Component Summary (Q3) GROUP BY device_id + type IN (...)
    # Rationale: when pivoting CPU/RAM/MAINBOARD per device, PostgreSQL can
    #            use this index to satisfy both the JOIN and the IN filter
    #            without a sequential scan on device_components.
    _run_autocommit("""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_dc_device_type
        ON device_components (device_id, component_type);
    """)

    # ── 3. device_components : idx_dc_specifications_gin ────────────────────
    # Used by: RAM Inventory (Q1) – JSONB extraction (specifications->>'capacity_gb')
    # Rationale: GIN index on the JSONB column lets PostgreSQL use index scan
    #            for operators like @> (containment) and ? (key existence).
    #            Without this, PostgreSQL falls back to a sequential scan and
    #            evaluates the ->> expression row by row.
    _run_autocommit("""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_dc_specifications_gin
        ON device_components USING GIN (specifications);
    """)

    # ── 4. software_installations : idx_si_device_deleted ───────────────────
    # Used by: Software Usage (Q2) – JOIN devices + soft-delete filter
    # Rationale: the query always starts from software_installations filtered
    #            by (device_id, deleted_at IS NULL).  Without this composite
    #            index the planner must seq-scan the whole table even when
    #            filtering a single device.
    _run_autocommit("""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_si_device_deleted
        ON software_installations (device_id, deleted_at);
    """)

    # ── 5. software_installations : idx_si_software_name ────────────────────
    # Used by: Software Usage (Q2) – exact filter by software_name
    # Rationale: supports equality filter (software_name = 'Microsoft Office 365')
    #            and prefix matching.  Works together with trgm index (below).
    _run_autocommit("""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_si_software_name
        ON software_installations (software_name);
    """)

    # ── 6. software_installations : idx_si_license_id ───────────────────────
    # Used by: Software Usage (Q2) – LEFT JOIN software_licenses ON license_id
    # Rationale: FK column without an explicit index causes a sequential scan
    #            on software_installations for every license lookup.
    _run_autocommit("""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_si_license_id
        ON software_installations (license_id);
    """)

    # ── 7. software_installations : idx_si_software_name_trgm (pg_trgm GIN) ─
    # Used by: Software Usage (Q2) blacklist JOIN / ILIKE search
    #          Also used by: blacklist detection (LicenseService.is_blacklisted)
    # Rationale: ILIKE '%Office%' or '%uTorrent%' cannot use a plain B-tree.
    #            GIN trigram index turns these into fast index scans regardless
    #            of whether the wildcard is leading, trailing, or both.
    _run_autocommit("""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_si_software_name_trgm
        ON software_installations USING GIN (software_name gin_trgm_ops);
    """)

    # ── 8. devices : idx_devices_assigned_deleted ───────────────────────────
    # Used by: RAM Inventory (Q1), Software Usage (Q2), Component Summary (Q3)
    # Rationale: all three reports walk the chain:
    #            device_components → devices → users → departments.
    #            This index covers the JOIN predicate (assigned_to_id) and the
    #            soft-delete guard (deleted_at IS NULL) simultaneously.
    _run_autocommit("""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_devices_assigned_deleted
        ON devices (assigned_to_id, deleted_at);
    """)


# ---------------------------------------------------------------------------
# downgrade
# ---------------------------------------------------------------------------
def downgrade() -> None:
    # Drop in reverse creation order.
    # CONCURRENTLY in DROP also avoids table locks.
    _run_autocommit("DROP INDEX CONCURRENTLY IF EXISTS idx_devices_assigned_deleted;")
    _run_autocommit("DROP INDEX CONCURRENTLY IF EXISTS idx_si_software_name_trgm;")
    _run_autocommit("DROP INDEX CONCURRENTLY IF EXISTS idx_si_license_id;")
    _run_autocommit("DROP INDEX CONCURRENTLY IF EXISTS idx_si_software_name;")
    _run_autocommit("DROP INDEX CONCURRENTLY IF EXISTS idx_si_device_deleted;")
    _run_autocommit("DROP INDEX CONCURRENTLY IF EXISTS idx_dc_specifications_gin;")
    _run_autocommit("DROP INDEX CONCURRENTLY IF EXISTS idx_dc_device_type;")
    _run_autocommit("DROP INDEX CONCURRENTLY IF EXISTS idx_dc_type_deleted;")

    # Note: we do NOT drop pg_trgm or uuid-ossp because other parts of the
    # schema may depend on them.  Remove manually if truly needed.
