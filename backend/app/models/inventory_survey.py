import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, UUIDMixin, TimestampMixin, SoftDeleteMixin

class InventorySurvey(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "inventory_surveys"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="OPEN") # OPEN, CLOSED, RECONCILED
    location_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("locations.id"))
    closed_at: Mapped[Optional[datetime]] = mapped_column()
    
    items: Mapped[List["SurveyItem"]] = relationship(back_populates="survey")

class SurveyItem(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "survey_items"

    survey_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("inventory_surveys.id"), nullable=False)
    device_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("devices.id"))
    asset_tag: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # MATCHED (at expected location), MISPLACED (found elsewhere), MISSING (not found in expected), UNKNOWN (not in DB)
    status: Mapped[str] = mapped_column(String(20), default="MATCHED")
    
    expected_location_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("locations.id"))
    actual_location_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("locations.id"), nullable=False)
    
    scanned_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    scanned_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))

    survey: Mapped["InventorySurvey"] = relationship(back_populates="items")
