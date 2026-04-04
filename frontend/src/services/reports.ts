/**
 * frontend/src/services/reports.ts
 * API client functions for Module 8 Reports & Export.
 */
import apiClient from './apiClient'

// ─── Filter interfaces ────────────────────────────────────────────────────

export interface RAMInventoryFilters {
  department_id?: string
  location_id?: string
  manufacturer?: string
  memory_type?: string       // 'DDR4' | 'DDR5'
  date_from?: string         // YYYY-MM-DD
  date_to?: string
}

export interface SoftwareUsageFilters {
  department_id?: string
  software_name?: string
  license_type?: string
  publisher?: string
  only_violations?: boolean
}

export interface ComponentFilters {
  department_id?: string
  location_id?: string
  component_types?: string[]
}

// ─── Response interfaces ──────────────────────────────────────────────────

export interface RAMComponentRow {
  device_id: string
  hostname?: string
  asset_tag?: string
  device_name?: string
  location_name?: string
  department?: string
  component_id: string
  slot_name?: string
  manufacturer?: string
  ram_model?: string
  component_serial?: string
  component_status?: string
  installation_date?: string
  capacity_gb?: number
  memory_type?: string
  speed_mhz?: number
  form_factor?: string
}

export interface RAMInventoryReport {
  generated_at: string
  total_records: number
  total_gb: number
  by_manufacturer: Record<string, number>
  by_department: Record<string, number>
  by_type: Record<string, number>
  by_location: Record<string, number>
  items: RAMComponentRow[]
}

export interface SoftwareInstallationRow {
  installation_id: string
  software_name: string
  version?: string
  publisher?: string
  install_date?: string
  hostname?: string
  asset_tag?: string
  department?: string
  department_id?: string
  license_type?: string
  total_seats?: number
  used_seats?: number
  license_expire_date?: string
  over_license: boolean
  is_blacklisted: boolean
  is_blocked: boolean
}

export interface SoftwareSummaryEntry {
  software_name: string
  total_installs: number
  by_version: Record<string, number>
  by_dept: Record<string, number>
}

export interface SoftwareUsageReport {
  generated_at: string
  total_records: number
  violation_count: number
  by_software: SoftwareSummaryEntry[]
  by_department: Record<string, number>
  violations: SoftwareInstallationRow[]
  items: SoftwareInstallationRow[]
}

export interface ComponentSummaryRow {
  device_id: string
  hostname?: string
  asset_tag?: string
  department?: string
  os_name?: string
  cpu_manufacturer?: string
  cpu_model?: string
  cpu_cores?: number
  total_ram_gb?: number
  ram_slots_used: number
  mainboard_manufacturer?: string
  mainboard_model?: string
  bios_version?: string
}

export interface ComponentSummaryReport {
  generated_at: string
  total_devices: number
  by_cpu_manufacturer: Record<string, number>
  by_ram_size: Record<string, number>
  by_mainboard_manufacturer: Record<string, number>
  items: ComponentSummaryRow[]
}

// ─── Helpers ──────────────────────────────────────────────────────────────

const cleanParams = (obj: Record<string, unknown>) =>
  Object.fromEntries(Object.entries(obj).filter(([, v]) => v != null && v !== '' && v !== false))

// ─── API calls ────────────────────────────────────────────────────────────

export const getRAMInventory = (filters: RAMInventoryFilters = {}) =>
  apiClient.get<RAMInventoryReport>('/reports/ram-inventory', {
    params: cleanParams(filters as Record<string, unknown>),
  })

export const getSoftwareUsage = (filters: SoftwareUsageFilters = {}) =>
  apiClient.get<SoftwareUsageReport>('/reports/software-usage', {
    params: cleanParams(filters as Record<string, unknown>),
  })

export const getComponentSummary = (filters: ComponentFilters = {}) =>
  apiClient.get<ComponentSummaryReport>('/reports/component-summary', {
    params: cleanParams(filters as Record<string, unknown>),
  })

/**
 * Download a report as Excel or PDF.
 * Returns a Blob that can be saved with FileSaver or <a> download.
 */
export const exportReport = (
  reportType: 'ram-inventory' | 'software-usage' | 'component-summary',
  format: 'excel' | 'pdf',
  filters: RAMInventoryFilters | SoftwareUsageFilters | ComponentFilters = {}
) =>
  apiClient.get(`/reports/export/${reportType}`, {
    params: { ...cleanParams(filters as Record<string, unknown>), format },
    responseType: 'blob',
  })
