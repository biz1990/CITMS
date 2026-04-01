import uuid
from typing import Optional, List, Dict
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class PurchaseOrderBase(BaseModel):
    title: str
    vendor_id: uuid.UUID
    status: str = "DRAFT"
    expected_delivery: Optional[datetime] = None
    notes: Optional[str] = None

class PurchaseOrderCreate(PurchaseOrderBase):
    pass

class PurchaseOrderUpdate(BaseModel):
    status: Optional[str] = None
    version: int

class PurchaseOrderResponse(PurchaseOrderBase):
    id: uuid.UUID
    po_number: str
    created_by: uuid.UUID
    created_at: datetime
    approved_by: Optional[uuid.UUID] = None
    version: int
    model_config = ConfigDict(from_attributes=True)
    
class ContractBase(BaseModel):
    contract_number: str
    title: str
    vendor_id: uuid.UUID
    start_date: datetime
    end_date: datetime
    value: float
    status: str = "ACTIVE"
    renewal_terms: Optional[str] = None

class ContractCreate(ContractBase):
    pass

class ContractResponse(ContractBase):
    id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)
