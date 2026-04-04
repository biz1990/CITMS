"""
app/api/routers/reports.py — Module 8: Reports & Export router.

Endpoints:
    GET  /reports/ram-inventory              → RAMInventoryReport (JSON)
    GET  /reports/software-usage             → SoftwareUsageReport (JSON)
    GET  /reports/component-summary          → ComponentSummaryReport (JSON)
    GET  /reports/export/ram-inventory       → Excel / PDF download
    GET  /reports/export/software-usage      → Excel / PDF download
    GET  /reports/export/component-summary   → Excel / PDF download
"""
from __future__ import annotations

import uuid
from datetime import date
from typing import Annotated, Any, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.api.auth_deps import RequireRole
from app.schemas.reports import (
    ComponentFilter,
    ComponentSummaryReport,
    RAMInventoryFilter,
    RAMInventoryReport,
    SoftwareUsageFilter,
    SoftwareUsageReport,
)
from app.services.reports_service import ReportsService

router = APIRouter()


# ============================================================================
# Dependency factories — parse Query params into filter models
# ============================================================================

def ram_inventory_filters(
    department_id: Optional[uuid.UUID] = Query(None, description="Filter by department UUID"),
    location_id:   Optional[uuid.UUID] = Query(None, description="Filter by location UUID"),
    manufacturer:  Optional[str]       = Query(None, description="Manufacturer substring, e.g. 'Samsung'"),
    memory_type:   Optional[str]       = Query(None, description="DDR4 or DDR5"),
    date_from:     Optional[date]      = Query(None, description="installation_date >= date_from (YYYY-MM-DD)"),
    date_to:       Optional[date]      = Query(None, description="installation_date <= date_to (YYYY-MM-DD)"),
) -> RAMInventoryFilter:
    return RAMInventoryFilter(
        department_id=department_id,
        location_id=location_id,
        manufacturer=manufacturer,
        memory_type=memory_type,
        date_from=date_from,
        date_to=date_to,
    )


def software_usage_filters(
    department_id:   Optional[uuid.UUID] = Query(None),
    software_name:   Optional[str]       = Query(None, description="Substring: 'Office', 'Chrome' …"),
    license_type:    Optional[str]       = Query(None, description="volume | subscription | OEM | freeware"),
    publisher:       Optional[str]       = Query(None, description="Publisher substring: 'Microsoft' …"),
    only_violations: bool                = Query(False, description="Return only over-license / blacklisted rows"),
) -> SoftwareUsageFilter:
    return SoftwareUsageFilter(
        department_id=department_id,
        software_name=software_name,
        license_type=license_type,
        publisher=publisher,
        only_violations=only_violations,
    )


def component_filters(
    department_id:   Optional[uuid.UUID] = Query(None),
    location_id:     Optional[uuid.UUID] = Query(None),
    component_types: list[str]           = Query(["CPU", "RAM", "MAINBOARD"]),
) -> ComponentFilter:
    return ComponentFilter(
        department_id=department_id,
        location_id=location_id,
        component_types=component_types,
    )


# ============================================================================
# Shared: format query param validator
# ============================================================================
ExportFormatQ = Annotated[
    Literal["excel", "pdf"],
    Query(description="Export format: 'excel' or 'pdf'"),
]

MIME_TYPES = {
    "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "pdf":   "application/pdf",
}
EXTENSIONS = {"excel": "xlsx", "pdf": "pdf"}


def _stream_export(content: bytes, filename: str, fmt: str) -> StreamingResponse:
    """Wrap raw bytes in a StreamingResponse with correct headers."""
    import io
    return StreamingResponse(
        io.BytesIO(content),
        media_type=MIME_TYPES[fmt],
        headers={"Content-Disposition": f'attachment; filename="{filename}.{EXTENSIONS[fmt]}"'},
    )


# ============================================================================
# GET /reports/ram-inventory
# ============================================================================
@router.get(
    "/ram-inventory",
    response_model=RAMInventoryReport,
    summary="RAM Inventory — detailed per-slot report",
    description=(
        "Returns a list of all active RAM modules across all devices, with "
        "JSONB-extracted specs (capacity_gb, memory_type, speed_mhz, form_factor). "
        "Supports filtering by department, location, manufacturer, and memory type. "
        "Results are cached in Redis for 15 minutes."
    ),
    tags=["Reports"],
)
async def get_ram_inventory(
    filters: RAMInventoryFilter  = Depends(ram_inventory_filters),
    db:      AsyncSession        = Depends(get_db),
    _:       Any                 = Depends(RequireRole("settings:read")),
) -> RAMInventoryReport:
    svc = ReportsService(db)
    return await svc.get_ram_inventory(filters)


# ============================================================================
# GET /reports/software-usage
# ============================================================================
@router.get(
    "/software-usage",
    response_model=SoftwareUsageReport,
    summary="Software Usage — per-device installation report with violation detection",
    description=(
        "Returns all software installations with license compliance flags "
        "(over_license, is_blacklisted, is_blocked). "
        "Supports filter by department, software name (ILIKE), license type, publisher. "
        "Set only_violations=true to get only non-compliant rows. "
        "Results are cached in Redis for 15 minutes."
    ),
    tags=["Reports"],
)
async def get_software_usage(
    filters: SoftwareUsageFilter = Depends(software_usage_filters),
    db:      AsyncSession        = Depends(get_db),
    _:       Any                 = Depends(RequireRole("settings:read")),
) -> SoftwareUsageReport:
    svc = ReportsService(db)
    return await svc.get_software_usage(filters)


# ============================================================================
# GET /reports/component-summary
# ============================================================================
@router.get(
    "/component-summary",
    response_model=ComponentSummaryReport,
    summary="Device Component Summary — CPU + RAM + Mainboard pivot per device",
    description=(
        "Pivots device_components rows (CPU, RAM, MAINBOARD) into one row per device "
        "using conditional aggregation. JSONB fields extracted: cores, threads, speed_ghz, "
        "capacity_gb, bios_version, bios_release_date. "
        "Results are cached in Redis for 15 minutes."
    ),
    tags=["Reports"],
)
async def get_component_summary(
    filters: ComponentFilter = Depends(component_filters),
    db:      AsyncSession    = Depends(get_db),
    _:       Any             = Depends(RequireRole("settings:read")),
) -> ComponentSummaryReport:
    svc = ReportsService(db)
    return await svc.get_component_summary(filters)


# ============================================================================
# GET /reports/export/ram-inventory
# ============================================================================
@router.get(
    "/export/ram-inventory",
    summary="Export RAM Inventory report (Excel or PDF)",
    tags=["Reports — Export"],
)
async def export_ram_inventory(
    format:  ExportFormatQ       = "excel",
    filters: RAMInventoryFilter  = Depends(ram_inventory_filters),
    db:      AsyncSession        = Depends(get_db),
    _:       Any                 = Depends(RequireRole("settings:read")),
) -> StreamingResponse:
    svc = ReportsService(db)
    if format == "excel":
        content = await svc.export_excel("ram_inventory", filters)
    else:
        content = await svc.export_pdf("ram_inventory", filters)
    return _stream_export(content, "ram_inventory_report", format)


# ============================================================================
# GET /reports/export/software-usage
# ============================================================================
@router.get(
    "/export/software-usage",
    summary="Export Software Usage report (Excel or PDF)",
    tags=["Reports — Export"],
)
async def export_software_usage(
    format:  ExportFormatQ        = "excel",
    filters: SoftwareUsageFilter  = Depends(software_usage_filters),
    db:      AsyncSession         = Depends(get_db),
    _:       Any                  = Depends(RequireRole("settings:read")),
) -> StreamingResponse:
    svc = ReportsService(db)
    if format == "excel":
        content = await svc.export_excel("software_usage", filters)
    else:
        content = await svc.export_pdf("software_usage", filters)
    return _stream_export(content, "software_usage_report", format)


# ============================================================================
# GET /reports/export/component-summary
# ============================================================================
@router.get(
    "/export/component-summary",
    summary="Export Component Summary report (Excel or PDF)",
    tags=["Reports — Export"],
)
async def export_component_summary(
    format:  ExportFormatQ    = "excel",
    filters: ComponentFilter  = Depends(component_filters),
    db:      AsyncSession     = Depends(get_db),
    _:       Any              = Depends(RequireRole("settings:read")),
) -> StreamingResponse:
    svc = ReportsService(db)
    if format == "excel":
        content = await svc.export_excel("component_summary", filters)
    else:
        content = await svc.export_pdf("component_summary", filters)
    return _stream_export(content, "component_summary_report", format)


# ============================================================================
# (Legacy) GET /reports/export/devices  — kept for backward compatibility
# ============================================================================
@router.get(
    "/export/devices",
    summary="[Legacy] CSV export of all devices",
    tags=["Reports — Export"],
    deprecated=True,
)
async def export_devices_legacy(
    db: AsyncSession = Depends(get_db),
    _:  Any          = Depends(RequireRole("settings:read")),
) -> StreamingResponse:
    import io
    output = io.StringIO()
    output.write("id,hostname,mac,status\n")
    output.write("Use /reports/component-summary for full hardware data.\n")
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=devices.csv"},
    )
