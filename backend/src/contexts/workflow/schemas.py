from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from backend.src.contexts.workflow.models import WorkflowStatus, WorkflowType

class WorkflowRequestBase(BaseModel):
    user_id: UUID
    type: WorkflowType
    effective_date: datetime
    notes: Optional[str] = None

class WorkflowRequestCreate(WorkflowRequestBase):
    pass

class WorkflowRequestResponse(WorkflowRequestBase):
    id: UUID
    status: WorkflowStatus
    requested_by: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

class WorkflowStatusUpdate(BaseModel):
    status: WorkflowStatus

class ApprovalRequest(BaseModel):
    comments: Optional[str] = None

class OnboardingCompleteRequest(BaseModel):
    device_ids: List[UUID]

class AssignmentResponse(BaseModel):
    id: UUID
    device_id: UUID
    user_id: UUID
    assigned_at: datetime
    returned_at: Optional[datetime] = None
    condition_on_assign: Optional[str] = None
    qr_code_token: Optional[str] = None
    
    class Config:
        from_attributes = True
