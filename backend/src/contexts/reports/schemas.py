from pydantic import BaseModel, Field
from typing import List, Optional, Any
from uuid import UUID
from datetime import datetime, date

class ReportFilter(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    category: Optional[str] = None
    status: Optional[str] = None
    user_id: Optional[UUID] = None
    action: Optional[str] = None
    type: Optional[str] = None
    format: str = Field(default="json", pattern="^(json|csv|xlsx|pdf)$")

class AssetInventoryReport(BaseModel):
    device_id: UUID
    hostname: str
    serial_number: Optional[str]
    device_type: str
    status: str
    assigned_to: Optional[str]
    last_seen: Optional[datetime]

class AssetDepreciationReport(BaseModel):
    device_id: UUID
    hostname: str
    purchase_price: float
    purchase_date: date
    age_months: int
    current_value: float
    depreciation_rate: float

class SoftwareComplianceReport(BaseModel):
    software_name: str
    total_installations: int
    total_seats: int
    available_seats: int
    is_violated: bool

class TicketSlaReport(BaseModel):
    priority: str
    total_tickets: int
    avg_resolution_time_hours: float
    breach_count: int
    sla_compliance_rate: float

class ReportExportResponse(BaseModel):
    download_url: str
    generated_at: datetime
