import uuid
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class SoftwareLicenseBase(BaseModel):
    software_name: str
    publisher: Optional[str] = None
    license_key: Optional[str] = None
    license_type: str = "PERPETUAL"
    total_seats: int
    expiry_date: Optional[datetime] = None

class SoftwareLicenseCreate(SoftwareLicenseBase):
    pass

class SoftwareLicenseResponse(SoftwareLicenseBase):
    id: uuid.UUID
    used_seats: int
    model_config = ConfigDict(from_attributes=True)

class SoftwareInstallationResponse(BaseModel):
    id: uuid.UUID
    device_id: uuid.UUID
    software_name: str
    version: str
    is_blocked: bool
    install_date: datetime
    license_id: Optional[uuid.UUID] = None
    model_config = ConfigDict(from_attributes=True)

class ViolationReportResponse(BaseModel):
    software_name: str
    total_seats: int
    used_seats: int
    excess: int
