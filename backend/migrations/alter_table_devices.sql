-- Migration: Add alternative_macs and auto_asset_tag to devices table
-- Author: CITMS Team
-- Date: 2026-04-08

-- 1. Add auto_asset_tag column
ALTER TABLE devices ADD COLUMN IF NOT EXISTS auto_asset_tag VARCHAR(50);

-- 2. Add alternative_macs column (JSONB to store history)
ALTER TABLE devices ADD COLUMN IF NOT EXISTS alternative_macs JSONB DEFAULT '[]'::jsonb;

-- 3. Add index for faster MAC lookup in JSONB
CREATE INDEX IF NOT EXISTS idx_devices_alternative_macs ON devices USING GIN (alternative_macs);

-- 4. Update existing invalid_serial devices with auto_asset_tag if empty
UPDATE devices 
SET auto_asset_tag = 'AUTO-' || REPLACE(primary_mac, ':', ''),
    asset_tag = COALESCE(asset_tag, 'AUTO-' || REPLACE(primary_mac, ':', ''))
WHERE invalid_serial = TRUE AND (auto_asset_tag IS NULL OR asset_tag IS NULL);

-- 5. Add comment for documentation
COMMENT ON COLUMN devices.alternative_macs IS 'History of all MAC addresses seen for this device, including USB dongles.';
COMMENT ON COLUMN devices.auto_asset_tag IS 'Automatically generated asset tag for devices with invalid serial numbers.';
