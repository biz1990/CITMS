-- Migration: Add Spare Parts and Inventory Tracking
-- Author: CITMS Team
-- Date: 2026-04-08

-- 1. Create spare_parts table
CREATE TABLE IF NOT EXISTS spare_parts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    manufacturer VARCHAR(100),
    quantity INTEGER DEFAULT 0,
    min_quantity INTEGER DEFAULT 5,
    unit_price NUMERIC(15, 2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- 2. Add spare_part_id to purchase_items
ALTER TABLE purchase_items ADD COLUMN IF NOT EXISTS spare_part_id UUID REFERENCES spare_parts(id);

-- 3. Add spare_parts_used to tickets (if not exists)
ALTER TABLE tickets ADD COLUMN IF NOT EXISTS spare_parts_used JSONB;

-- 4. Create Materialized View for Inventory Summary (if not exists)
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_inventory_summary AS
SELECT 
    device_type,
    device_subtype,
    status,
    COUNT(*) as device_count,
    MIN(last_seen) as oldest_seen,
    MAX(last_seen) as newest_seen
FROM devices
WHERE deleted_at IS NULL
GROUP BY device_type, device_subtype, status;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_inventory_summary ON mv_inventory_summary (device_type, device_subtype, status);
