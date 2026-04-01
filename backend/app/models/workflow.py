import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, ForeignKey, Boolean, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB, INET, UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, UUIDMixin, TimestampMixin, SoftDeleteMixin

class DeviceAssignment(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "device_assignments"

    device_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("devices.id"))
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id"))
    assignment_type: Mapped[Optional[str]] = mapped_column(String(20))
    assigned_at: Mapped[Optional[datetime]] = mapped_column()
    returned_at: Mapped[Optional[datetime]] = mapped_column()
    assigned_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id"))
    return_condition: Mapped[Optional[str]] = mapped_column(String(20))
    notes: Mapped[Optional[str]] = mapped_column(Text)


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id"))
    title: Mapped[Optional[str]] = mapped_column(String(200))
    message: Mapped[Optional[str]] = mapped_column(Text)
    type: Mapped[Optional[str]] = mapped_column(String(20))
    channel: Mapped[Optional[str]] = mapped_column(String(20))
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    related_entity_type: Mapped[Optional[str]] = mapped_column(String(50))
    related_entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), nullable=False)


class WorkflowRequest(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "workflow_requests"

    request_type: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default='PENDING_IT')
    requested_by: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id"))
    target_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id"))
    template_details: Mapped[Optional[dict]] = mapped_column(JSONB)
    completed_at: Mapped[Optional[datetime]] = mapped_column()


class ApprovalHistory(Base):
    __tablename__ = "approval_history"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    action: Mapped[str] = mapped_column(String(20), nullable=False)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id"))
    comment: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), nullable=False)


class HistoryLog(Base):
    """
    This table will be partitioned by RANGE(created_at).
    """
    __tablename__ = "history_logs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True, default=func.now())
    table_name: Mapped[str] = mapped_column(String(50), nullable=False)
    record_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    action: Mapped[str] = mapped_column(String(20), nullable=False)
    old_value: Mapped[Optional[dict]] = mapped_column(JSONB)
    new_value: Mapped[Optional[dict]] = mapped_column(JSONB)
    changed_by_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id"))
    ip_address: Mapped[Optional[str]] = mapped_column(INET)
    user_agent: Mapped[Optional[str]] = mapped_column(String(255))
    request_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
