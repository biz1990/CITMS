from sqlalchemy import String, ForeignKey, DateTime, Boolean, Integer, LargeBinary, text, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, BYTEA
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.src.infrastructure.models.base import CITMSBaseModel
from typing import Optional, List
from datetime import datetime
import uuid

class SoftwareLicense(CITMSBaseModel):
    __tablename__ = "software_licenses"
    __table_args__ = (
        CheckConstraint('used_seats >= 0', name='check_used_seats_non_negative'),
        CheckConstraint('total_seats > 0', name='check_total_seats_positive'),
    )
    
    software_catalog_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("software_catalog.id"))
    license_key_enc: Mapped[Optional[bytes]] = mapped_column(BYTEA)
    type: Mapped[str] = mapped_column(String(30)) # PERPETUAL, SUBSCRIPTION, OPEN_SOURCE
    total_seats: Mapped[int] = mapped_column(Integer, default=0)
    used_seats: Mapped[int] = mapped_column(Integer, default=0)
    purchase_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    expire_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    vendor_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("vendors.id"))
    
    # Relationships
    installations: Mapped[List["SoftwareInstallation"]] = relationship(back_populates="license")

class SerialBlacklist(CITMSBaseModel):
    __tablename__ = "serial_blacklist"
    serial_number: Mapped[str] = mapped_column(String(100), nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(String)

class SoftwareBlacklist(CITMSBaseModel):
    __tablename__ = "software_blacklist"
    software_name: Mapped[str] = mapped_column(String(100), nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(String)
