import uuid
from datetime import datetime, date
from typing import Optional
from sqlalchemy import String, Integer, ForeignKey, Boolean, Date, LargeBinary, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, UUIDMixin, TimestampMixin, SoftDeleteMixin

class SoftwareCatalog(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "software_catalog"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    regex_pattern: Mapped[Optional[str]] = mapped_column(String(255)) # v3.6 §4.1
    description: Mapped[Optional[str]] = mapped_column(Text)

class SoftwareLicense(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "software_licenses"

    software_name: Mapped[Optional[str]] = mapped_column(String(100))
    license_key_enc: Mapped[Optional[bytes]] = mapped_column(LargeBinary)
    type: Mapped[Optional[str]] = mapped_column(String(30))
    total_seats: Mapped[Optional[int]] = mapped_column(Integer)
    used_seats: Mapped[int] = mapped_column(Integer, default=0)
    purchase_date: Mapped[Optional[date]] = mapped_column(Date)
    expire_date: Mapped[Optional[date]] = mapped_column(Date)
    vendor_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("vendors.id"))


class SoftwareInstallation(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "software_installations"

    device_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("devices.id"))
    software_catalog_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("software_catalog.id")) # v3.6 §4.1
    software_name: Mapped[Optional[str]] = mapped_column(String(100))
    version: Mapped[Optional[str]] = mapped_column(String(50))
    publisher: Mapped[Optional[str]] = mapped_column(String(100))
    install_date: Mapped[Optional[date]] = mapped_column(Date)
    license_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("software_licenses.id"))
    is_blocked: Mapped[Optional[bool]] = mapped_column(Boolean)


class SerialBlacklist(Base):
    __tablename__ = "serial_blacklist"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    serial_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(Text)
    from sqlalchemy import DateTime
    from sqlalchemy.sql import func
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), nullable=False)


class SoftwareBlacklist(Base):
    __tablename__ = "software_blacklist"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    software_name: Mapped[Optional[str]] = mapped_column(String(100))
    reason: Mapped[Optional[str]] = mapped_column(Text)
    from sqlalchemy import DateTime
    from sqlalchemy.sql import func
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), nullable=False)
