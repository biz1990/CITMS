-- Migration: Add fields for industrial devices and peripherals
-- Author: CITMS Team
-- Date: 2026-04-08

-- 1. Add new_peripheral to device_components
ALTER TABLE device_components ADD COLUMN IF NOT EXISTS new_peripheral BOOLEAN DEFAULT FALSE;

-- 2. Add baud_rate to devices (for COM scanners)
ALTER TABLE devices ADD COLUMN IF NOT EXISTS baud_rate INTEGER;

-- 3. Add port_name and slot_name to device_connections
ALTER TABLE device_connections ADD COLUMN IF NOT EXISTS port_name VARCHAR(50);
ALTER TABLE device_connections ADD COLUMN IF NOT EXISTS slot_name VARCHAR(50);

-- 4. Add comments
COMMENT ON COLUMN device_components.new_peripheral IS 'Flag to mark newly detected peripherals for admin review.';
COMMENT ON COLUMN devices.baud_rate IS 'Baud rate for devices connected via COM port.';
COMMENT ON COLUMN device_connections.port_name IS 'Name of the port used for the connection (e.g., COM1, USB0).';
COMMENT ON COLUMN device_connections.slot_name IS 'Name of the slot used for the connection (e.g., PCIe Slot 1).';
