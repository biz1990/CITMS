from sqlalchemy import String, ForeignKey, DateTime, Boolean, Integer, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.src.infrastructure.models.base import CITMSBaseModel
from typing import Optional, List
from datetime import datetime
import uuid
import enum

class WorkflowType(str, enum.Enum):
    ONBOARDING = "ONBOARDING"
    OFFBOARDING = "OFFBOARDING"
    REPLACEMENT = "REPLACEMENT"

class WorkflowStatus(str, enum.Enum):
    PENDING_IT = "PENDING_IT"
    PREPARING = "PREPARING"
    READY_FOR_PICKUP = "READY_FOR_PICKUP"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class WorkflowRequest(CITMSBaseModel):
    __tablename__ = "workflow_requests"
    
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    type: Mapped[WorkflowType] = mapped_column(String(30))
    status: Mapped[WorkflowStatus] = mapped_column(String(30), default=WorkflowStatus.PENDING_IT)
    requested_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    effective_date: Mapped[datetime] = mapped_column(DateTime)
    notes: Mapped[Optional[str]] = mapped_column(text)
    
    # Relationships
    approvals: Mapped[List["ApprovalHistory"]] = relationship(back_populates="request")

class DeviceAssignment(CITMSBaseModel):
    __tablename__ = "device_assignments"
    
    device_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("devices.id"))
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    assigned_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    returned_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    condition_on_assign: Mapped[Optional[str]] = mapped_column(String)
    condition_on_return: Mapped[Optional[str]] = mapped_column(String)
    qr_code_token: Mapped[Optional[str]] = mapped_column(String(100))

class ApprovalHistory(CITMSBaseModel):
    __tablename__ = "approval_history"
    
    request_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workflow_requests.id"))
    approver_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(String(20)) # APPROVED, REJECTED
    comments: Mapped[Optional[str]] = mapped_column(text)
    step_name: Mapped[Optional[str]] = mapped_column(String(50))
    
    request: Mapped["WorkflowRequest"] = relationship(back_populates="approvals")
