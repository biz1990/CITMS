from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

class LicenseBase(BaseModel):
    software_catalog_id: UUID
    type: str # PERPETUAL, SUBSCRIPTION, OPEN_SOURCE
    total_seats: int
    purchase_date: Optional[datetime] = None
    expire_date: Optional[datetime] = None
    vendor_id: Optional[UUID] = None

class LicenseCreate(LicenseBase):
    license_key: Optional[str] = None # Plaintext for input, encrypted in DB

class LicenseResponse(LicenseBase):
    id: UUID
    used_seats: int
    is_violated: bool = False
    class Config:
        from_attributes = True

class BlacklistBase(BaseModel):
    reason: Optional[str] = None

class SerialBlacklistCreate(BlacklistBase):
    serial_number: str

class SoftwareBlacklistCreate(BlacklistBase):
    software_name: str

class ViolationCheckResponse(BaseModel):
    violated_licenses: List[LicenseResponse]
    blacklisted_software_detected: List[str]
    blacklisted_serials_detected: List[str]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
