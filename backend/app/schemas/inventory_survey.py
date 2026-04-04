import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict

class SurveyItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    asset_tag: str
    status: str
    expected_location_id: Optional[uuid.UUID]
    actual_location_id: uuid.UUID
    scanned_at: datetime

class InventorySurveyCreate(BaseModel):
    name: str
    location_id: Optional[uuid.UUID] = None

class InventorySurveyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    status: str
    location_id: Optional[uuid.UUID]
    created_at: datetime
    closed_at: Optional[datetime]
    items: Optional[List[SurveyItemResponse]] = []

class ScanSubmit(BaseModel):
    asset_tag: str
    actual_location_id: uuid.UUID
