import uuid
from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime

# Vendor
class VendorBase(BaseModel):
    name: str
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    support_portal: Optional[str] = None

class VendorCreate(VendorBase):
    pass

class VendorResponse(VendorBase):
    id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)

# Spare Parts
class SparePartBase(BaseModel):
    part_number: str
    name: str
    description: Optional[str] = None
    category: str
    quantity: int = 0
    unit_price: float = 0.0
    critical_level: int = 1
    reorder_threshold: int = 5
    location_id: Optional[uuid.UUID] = None

class SparePartCreate(SparePartBase):
    vendor_id: Optional[uuid.UUID] = None

class SparePartUpdate(BaseModel):
    quantity: Optional[int] = None
    unit_price: Optional[float] = None
    reorder_threshold: Optional[int] = None

class SparePartResponse(SparePartBase):
    id: uuid.UUID
    vendor_id: Optional[uuid.UUID] = None
    total_value: float # computed
    model_config = ConfigDict(from_attributes=True)
