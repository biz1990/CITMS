import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, DECIMAL, ForeignKey, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, UUIDMixin, TimestampMixin, SoftDeleteMixin, OptimisticLockMixin

class Ticket(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin, OptimisticLockMixin):
    __tablename__ = "tickets"

    ticket_code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[Optional[str]] = mapped_column(String(30), default='OPEN')
    priority: Mapped[Optional[str]] = mapped_column(String(20), default='MEDIUM')
    category: Mapped[Optional[str]] = mapped_column(String(50))
    impact: Mapped[Optional[str]] = mapped_column(String(20))
    urgency: Mapped[Optional[str]] = mapped_column(String(20))
    
    is_change: Mapped[bool] = mapped_column(Boolean, default=False)
    change_type: Mapped[Optional[str]] = mapped_column(String(50))
    change_plan: Mapped[Optional[str]] = mapped_column(Text)
    rollback_plan: Mapped[Optional[str]] = mapped_column(Text)
    
    cab_approval_status: Mapped[Optional[str]] = mapped_column(String(20))
    cab_approved_by: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id"))
    cab_approved_at: Mapped[Optional[datetime]] = mapped_column()
    
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id"))
    assigned_to_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id"))
    device_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("devices.id"))
    location_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("locations.id"))
    vendor_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("vendors.id"))
    
    estimated_cost: Mapped[Optional[float]] = mapped_column(DECIMAL(12, 2))
    actual_cost: Mapped[Optional[float]] = mapped_column(DECIMAL(12, 2))
    
    sla_response_due: Mapped[Optional[datetime]] = mapped_column()
    sla_resolution_due: Mapped[Optional[datetime]] = mapped_column()
    resolution_notes: Mapped[Optional[str]] = mapped_column(Text)
    due_date: Mapped[Optional[datetime]] = mapped_column()


class TicketComment(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "ticket_comments"

    ticket_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("tickets.id"))
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id"))
    content: Mapped[Optional[str]] = mapped_column(Text)
    is_internal: Mapped[Optional[bool]] = mapped_column(Boolean)


class MaintenanceLog(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "maintenance_logs"

    device_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("devices.id"))
    ticket_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("tickets.id"))
    action_type: Mapped[Optional[str]] = mapped_column(String(50))
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # Needs to be imported inside or passed directly
    from sqlalchemy.dialects.postgresql import JSONB
    old_component_details: Mapped[Optional[dict]] = mapped_column(JSONB)
    new_component_details: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    performed_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id"))
    spare_part_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("spare_parts_inventory.id"))
    quantity_used: Mapped[Optional[int]] = mapped_column(Integer)
    cost: Mapped[Optional[float]] = mapped_column(DECIMAL(12, 2))
    status: Mapped[Optional[str]] = mapped_column(String(20))
