import uuid
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class WorkflowRequestBase(BaseModel):
    workflow_type: str # ONBOARDING, OFFBOARDING, ACCESS_GRANT
    target_user_id: Optional[uuid.UUID] = None
    template_details: Dict[str, Any] = {}

class WorkflowRequestCreate(WorkflowRequestBase):
    pass

class WorkflowRequestResponse(WorkflowRequestBase):
    id: uuid.UUID
    status: str
    created_by: uuid.UUID
    created_at: datetime
    completed_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class DeviceAssignmentResponse(BaseModel):
    id: uuid.UUID
    device_id: uuid.UUID
    user_id: uuid.UUID
    assignment_type: str
    return_condition: Optional[str] = None
    assigned_at: datetime
    returned_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)
