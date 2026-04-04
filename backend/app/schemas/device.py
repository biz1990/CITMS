import uuid
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict
from datetime import datetime

# Connection Schemas
class DeviceConnectionBase(BaseModel):
    connection_type: str
    port_name: Optional[str] = None
    target_device_id: uuid.UUID

class DeviceConnectionCreate(DeviceConnectionBase):
    pass

class DeviceConnectionResponse(DeviceConnectionBase):
    id: uuid.UUID
    source_device_id: uuid.UUID
    connected_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Device Schemas
class DeviceBase(BaseModel):
    name: Optional[str] = None
    serial_number: str
    asset_tag: Optional[str] = None
    primary_mac: Optional[str] = None
    device_type: str
    device_subtype: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    status: str = "IN_USE"
    location_id: Optional[uuid.UUID] = None
    warranty_expiry_date: Optional[datetime] = None
    rustdesk_id: Optional[str] = None
    rustdesk_password: Optional[str] = None

class DeviceCreate(DeviceBase):
    pass

class DeviceUpdate(BaseModel):
    name: Optional[str] = None
    asset_tag: Optional[str] = None
    status: Optional[str] = None
    location_id: Optional[uuid.UUID] = None
    warranty_expiry_date: Optional[datetime] = None
    rustdesk_id: Optional[str] = None
    rustdesk_password: Optional[str] = None
    version: int

class DeviceResponse(DeviceBase):
    id: uuid.UUID
    uuid_str: str
    last_seen: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    version: int
    
    agent_token_hash: Optional[str] = None
    last_reconciled_at: Optional[datetime] = None
    
    connections: List[DeviceConnectionResponse] = []
    
    model_config = ConfigDict(from_attributes=True)
    
class ReconcileRequest(BaseModel):
    run_id: str
    devices: List[Dict[str, Any]]

class RemoteSessionResponse(BaseModel):
    rustdesk_id: str
    temporary_session_token: str
    expires_at: datetime
