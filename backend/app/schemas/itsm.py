import uuid
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class TicketCommentBase(BaseModel):
    content: str
    is_internal: bool = False

class TicketCommentCreate(TicketCommentBase):
    pass

class TicketCommentResponse(TicketCommentBase):
    id: uuid.UUID
    ticket_id: uuid.UUID
    author_id: uuid.UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class TicketBase(BaseModel):
    title: str
    description: str
    priority: str = "MEDIUM"
    category: str
    device_id: Optional[uuid.UUID] = None

class TicketCreate(TicketBase):
    pass

class TicketUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_to_id: Optional[uuid.UUID] = None
    resolution_notes: Optional[str] = None
    version: int

class TicketResponse(TicketBase):
    id: uuid.UUID
    ticket_code: str
    status: str
    created_by: uuid.UUID
    assigned_to_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime
    sla_response_due: Optional[datetime] = None
    sla_resolution_due: Optional[datetime] = None
    version: int
    
    comments: List[TicketCommentResponse] = []
    model_config = ConfigDict(from_attributes=True)
