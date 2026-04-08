from sqlalchemy import String, ForeignKey, DateTime, Boolean, Integer, text, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.src.infrastructure.models.base import CITMSBaseModel
from typing import Optional, List
from datetime import datetime
import uuid
import enum

class TicketStatus(str, enum.Enum):
    OPEN = "OPEN"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    PENDING = "PENDING"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"

class TicketPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class Ticket(CITMSBaseModel):
    __tablename__ = "tickets"
    
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(text)
    status: Mapped[TicketStatus] = mapped_column(String(30), default=TicketStatus.OPEN)
    priority: Mapped[TicketPriority] = mapped_column(String(20), default=TicketPriority.MEDIUM)
    category: Mapped[Optional[str]] = mapped_column(String(50))
    
    reporter_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    assignee_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id"))
    department_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("departments.id"))
    location_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("locations.id"))
    device_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("devices.id"))
    vendor_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("vendors.id"))
    
    # SLA Fields
    sla_deadline: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    is_sla_breached: Mapped[bool] = mapped_column(Boolean, default=False)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Change Management
    is_change_request: Mapped[bool] = mapped_column(Boolean, default=False)
    change_plan: Mapped[Optional[str]] = mapped_column(text)
    rollback_plan: Mapped[Optional[str]] = mapped_column(text)
    cab_approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    cab_approver_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id"))
    
    # Relationships
    comments: Mapped[List["TicketComment"]] = relationship(back_populates="ticket", cascade="all, delete-orphan")
    maintenance_logs: Mapped[List["MaintenanceLog"]] = relationship(back_populates="ticket")

class TicketComment(CITMSBaseModel):
    __tablename__ = "ticket_comments"
    
    ticket_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tickets.id"))
    author_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    content: Mapped[str] = mapped_column(text)
    is_internal: Mapped[bool] = mapped_column(Boolean, default=False)
    attachments: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    ticket: Mapped["Ticket"] = relationship(back_populates="comments")

class MaintenanceLog(CITMSBaseModel):
    __tablename__ = "maintenance_logs"
    
    device_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("devices.id"))
    ticket_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("tickets.id"))
    technician_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    action_taken: Mapped[str] = mapped_column(text)
    spare_parts_used: Mapped[Optional[dict]] = mapped_column(JSONB)
    cost: Mapped[float] = mapped_column(Integer, default=0) # In minor units or decimal
    maintenance_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    ticket: Mapped["Ticket"] = relationship(back_populates="maintenance_logs")

class SystemHoliday(CITMSBaseModel):
    __tablename__ = "system_holidays"
    holiday_date: Mapped[datetime] = mapped_column(DateTime, unique=True)
    description: Mapped[str] = mapped_column(String(200))
