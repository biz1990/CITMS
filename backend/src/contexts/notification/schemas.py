from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

class NotificationResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    message: str
    event_type: str
    priority: str
    is_read: bool
    link: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class MarkReadRequest(BaseModel):
    notification_id: UUID
