from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

class TemporarySessionResponse(BaseModel):
    device_id: UUID
    rustdesk_id: str
    session_token: str
    expires_at: datetime
    relay_server: str
    webrtc_config: Optional[dict] = None

class RustDeskWebhookPayload(BaseModel):
    event: str # login, logout, status
    id: str    # rustdesk_id
    uuid: Optional[str] = None
    ip: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class DevicePreviewResponse(BaseModel):
    device_id: UUID
    preview_url: str
    timestamp: datetime

