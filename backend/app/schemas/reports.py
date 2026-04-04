"""
app/schemas/reports.py — Pydantic schemas for Module 8 Reports & Export.

Covers:
    • Input filter models (used as FastAPI Query dependencies)
    • Output row models (per record)
    • Output report models (aggregated response)
"""
from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ============================================================================
# Shared config
# ============================================================================
class _BaseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# ============================================================================
# FILTER models  (parsed from FastAPI Query params)
# ============================================================================

class RAMInventoryFilter(BaseModel):
    """Query parameters for GET /reports/ram-inventory"""
    department_id: Optional[uuid.UUID] = Field(None, description="Filter by department UUID")
    location_id:   Optional[uuid.UUID] = Field(None, description="Filter by location UUID (device.location_id)")
    manufacturer:  Optional[str]       = Field(None, description="Case-insensitive manufacturer substring, e.g. 'Samsung'")
    memory_type:   Optional[str]       = Field(None, description="DDR4 or DDR5")
    date_from:     Optional[date]      = Field(None, description="installation_date >= date_from")
    date_to:       Optional[date]      = Field(None, description="installation_date <= date_to")


class SoftwareUsageFilter(BaseModel):
    """Query parameters for GET /reports/software-usage"""
    department_id:   Optional[uuid.UUID] = Field(None)
    software_name:   Optional[str]       = Field(None, description="Substring search: 'Office', 'Chrome' …")
    license_type:    Optional[str]       = Field(None, description="volume | subscription | OEM | freeware")
    publisher:       Optional[str]       = Field(None, description="Substring: 'Microsoft' …")
    only_violations: bool                = Field(False, description="If true, return only over-license / blacklisted rows")


class ComponentFilter(BaseModel):
    """Query parameters for GET /reports/component-summary"""
    department_id: Optional[uuid.UUID] = Field(None)
    location_id:   Optional[uuid.UUID] = Field(None)
    component_types: list[str]         = Field(
        default=["CPU", "RAM", "MAINBOARD"],
        description="Which component types to pivot"
    )

class AssetOverviewFilter(BaseModel):
    location_id: Optional[uuid.UUID] = None
    device_type: Optional[str] = None
    status: Optional[str] = None

class RepairCostFilter(BaseModel):
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    department_id: Optional[uuid.UUID] = None
    vendor_id: Optional[uuid.UUID] = None

class ProcurementFilter(BaseModel):
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    status: Optional[str] = None


# ============================================================================
# RAM INVENTORY report
# ============================================================================

class RAMComponentRow(_BaseOut):
    """One RAM module on one device."""
    device_id:         uuid.UUID
    hostname:          Optional[str] = None
    asset_tag:         Optional[str] = None
    device_name:       Optional[str] = None
    location_name:     Optional[str] = None
    department:        Optional[str] = None
    # Component fields
    component_id:      uuid.UUID
    slot_name:         Optional[str]   = None   # DIMM_A1, DIMM_B2 …
    manufacturer:      Optional[str]   = None   # Samsung, Kingston …
    ram_model:         Optional[str]   = None   # e.g. "M471A2G43AB2-CWE"
    component_serial:  Optional[str]   = None
    component_status:  Optional[str]   = None   # active / removed
    installation_date: Optional[date]  = None
    # JSONB-extracted fields
    capacity_gb:       Optional[float] = None   # 8 / 16 / 32 …
    memory_type:       Optional[str]   = None   # DDR4 / DDR5
    speed_mhz:         Optional[int]   = None   # 3200 / 4800 / 5600
    form_factor:       Optional[str]   = None   # DIMM / SO-DIMM


class RAMInventoryReport(BaseModel):
    """Full RAM inventory report returned by the API."""
    generated_at:    datetime
    total_records:   int
    total_gb:        float
    by_manufacturer: dict[str, float]    # manufacturer  → total GB
    by_department:   dict[str, float]    # department    → total GB
    by_type:         dict[str, int]      # DDR4 / DDR5   → count
    by_location:     dict[str, float]    # location name → total GB
    items:           list[RAMComponentRow]


# ============================================================================
# SOFTWARE USAGE report
# ============================================================================

class SoftwareInstallationRow(_BaseOut):
    """One software installation on one device."""
    installation_id:      uuid.UUID
    software_name:        str
    version:              Optional[str]  = None
    publisher:            Optional[str]  = None
    install_date:         Optional[date] = None
    hostname:             Optional[str]  = None
    asset_tag:            Optional[str]  = None
    device_name:          Optional[str]  = None
    department:           Optional[str]  = None
    department_id:        Optional[uuid.UUID] = None
    # License info
    license_id:           Optional[uuid.UUID] = None
    license_type:         Optional[str]  = None    # volume / subscription / OEM
    total_seats:          Optional[int]  = None
    used_seats:           Optional[int]  = None
    license_expire_date:  Optional[date] = None
    # Violation flags
    over_license:         bool = False   # used_seats > total_seats
    is_blacklisted:       bool = False   # EXISTS in software_blacklist
    is_blocked:           bool = False   # is_blocked column on installation


class SoftwareSummaryEntry(BaseModel):
    """Aggregate counts for one software name."""
    software_name:  str
    total_installs: int
    by_version:     dict[str, int]   # {"365": 30, "2021": 15, "N/A": 2}
    by_dept:        dict[str, int]   # {"IT": 10, "Finance": 5}


class SoftwareUsageReport(BaseModel):
    """Full software usage report returned by the API."""
    generated_at:    datetime
    total_records:   int
    violation_count: int
    by_software:     list[SoftwareSummaryEntry]   # sorted by total_installs desc
    by_department:   dict[str, int]               # dept name → total installs
    violations:      list[SoftwareInstallationRow]
    items:           list[SoftwareInstallationRow]


# ============================================================================
# COMPONENT SUMMARY report  (CPU + RAM + MAINBOARD pivot per device)
# ============================================================================

class ComponentSummaryRow(_BaseOut):
    """Pivoted hardware summary for one device."""
    device_id:   uuid.UUID
    hostname:    Optional[str] = None
    asset_tag:   Optional[str] = None
    device_name: Optional[str] = None
    department:  Optional[str] = None
    os_name:     Optional[str] = None
    # CPU — max() across matching rows
    cpu_manufacturer: Optional[str]   = None
    cpu_model:        Optional[str]   = None
    cpu_cores:        Optional[int]   = None
    cpu_threads:      Optional[int]   = None
    cpu_speed_ghz:    Optional[float] = None
    # RAM — aggregate across RAM slots
    total_ram_gb:     Optional[float] = None
    ram_slots_used:   int             = 0
    # Mainboard
    mainboard_manufacturer: Optional[str] = None
    mainboard_model:        Optional[str] = None
    bios_version:           Optional[str] = None
    bios_release_date:      Optional[str] = None


class ComponentSummaryReport(BaseModel):
    """Full component summary report."""
    generated_at:              datetime
    total_devices:             int
    by_cpu_manufacturer:       dict[str, int]    # Intel → 80, AMD → 20
    by_ram_size:               dict[str, int]    # "16GB" → 45, "32GB" → 30
    by_mainboard_manufacturer: dict[str, int]
    items:                     list[ComponentSummaryRow]

# --- New Reports for Module 8 (SRS 8.1) ---

class AssetOverviewEntry(BaseModel):
    device_type: str
    count: int
    by_status: dict[str, int]

class AssetOverviewReport(BaseModel):
    generated_at: datetime
    total_assets: int
    overview: list[AssetOverviewEntry]
    by_location: dict[str, int]

class AssetDepreciationRow(BaseModel):
    asset_tag: str
    name: str
    purchase_date: Optional[date]
    purchase_cost: float
    current_value: float
    depreciation_method: str
    age_months: int

class AssetDepreciationReport(BaseModel):
    generated_at: datetime
    total_purchase_cost: float
    total_current_value: float
    items: list[AssetDepreciationRow]

class InventoryStatusRow(BaseModel):
    name: str
    category: str
    quantity: int
    min_quantity: int
    unit_cost: float
    total_value: float
    is_low_stock: bool

class InventoryStatusReport(BaseModel):
    generated_at: datetime
    total_value: float
    low_stock_count: int
    items: list[InventoryStatusRow]

class TicketSLARow(BaseModel):
    ticket_code: str
    title: str
    priority: str
    created_at: datetime
    resolved_at: Optional[datetime]
    sla_resolution_due: Optional[datetime]
    is_breached: bool
    resolution_time_hours: Optional[float]

class TicketSLAReport(BaseModel):
    generated_at: datetime
    total_tickets: int
    breach_count: int
    avg_resolution_time_hours: float
    by_priority: dict[str, dict[str, Any]] # { "HIGH": {"count": 10, "breaches": 1} }
    items: list[TicketSLARow]


# ============================================================================
# Export meta
# ============================================================================
class ExportFormat(str):
    EXCEL = "excel"
    PDF   = "pdf"
