from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from backend.src.contexts.procurement.models import POStatus

class POItemBase(BaseModel):
    item_name: str
    quantity: int
    unit_price: float

class POItemCreate(POItemBase):
    pass

class POItemResponse(POItemBase):
    id: UUID
    received_quantity: int
    class Config:
        from_attributes = True

class POCreate(BaseModel):
    vendor_id: UUID
    po_number: str
    items: List[POItemCreate]

class POResponse(BaseModel):
    id: UUID
    po_number: str
    vendor_id: UUID
    status: POStatus
    total_amount: float
    requested_by: UUID
    approved_by: Optional[UUID] = None
    items: List[POItemResponse]
    created_at: datetime
    
    class Config:
        from_attributes = True

class POStatusUpdate(BaseModel):
    status: POStatus

class ReceiveItemRequest(BaseModel):
    item_id: UUID
    quantity: int

class VendorBase(BaseModel):
    name: str
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    tax_code: Optional[str] = None

class VendorResponse(VendorBase):
    id: UUID
    class Config:
        from_attributes = True
