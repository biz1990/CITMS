-- Migration: Add invalid_serial to device_components
ALTER TABLE device_components ADD COLUMN invalid_serial BOOLEAN DEFAULT FALSE;

COMMENT ON COLUMN device_components.invalid_serial IS 'Flag to mark components with invalid or cloned serial numbers';
