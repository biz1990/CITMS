import uuid
from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import String, Integer, DECIMAL, ForeignKey, Boolean, Date, Text, LargeBinary, CheckConstraint
from sqlalchemy.dialects.postgresql import INET, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, UUIDMixin, TimestampMixin, SoftDeleteMixin, OptimisticLockMixin

class Device(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin, OptimisticLockMixin):
    __tablename__ = "devices"

    asset_tag: Mapped[Optional[str]] = mapped_column(String(50))
    name: Mapped[Optional[str]] = mapped_column(String(100))
    device_type: Mapped[Optional[str]] = mapped_column(String(50))
    device_subtype: Mapped[Optional[str]] = mapped_column(String(30))
    manufacturer: Mapped[Optional[str]] = mapped_column(String(100))
    model: Mapped[Optional[str]] = mapped_column(String(100))
    serial_number: Mapped[Optional[str]] = mapped_column(String(100))
    uuid_str: Mapped[Optional[str]] = mapped_column("uuid", String(36)) # DB column named 'uuid'
    primary_mac: Mapped[Optional[str]] = mapped_column(String(17))
    hostname: Mapped[Optional[str]] = mapped_column(String(100))
    network_ipv4: Mapped[Optional[str]] = mapped_column(INET)
    os_name: Mapped[Optional[str]] = mapped_column(String(50))
    os_version: Mapped[Optional[str]] = mapped_column(String(50))
    status: Mapped[Optional[str]] = mapped_column(String(30))
    
    assigned_to_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id"))
    location_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("locations.id"))
    purchase_item_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("purchase_items.id"))
    
    purchase_date: Mapped[Optional[date]] = mapped_column(Date)
    purchase_cost: Mapped[Optional[float]] = mapped_column(DECIMAL(12, 2))
    depreciation_method: Mapped[Optional[str]] = mapped_column(String(20))
    
    rustdesk_id: Mapped[Optional[str]] = mapped_column(String(50))
    rustdesk_password_enc: Mapped[Optional[bytes]] = mapped_column(LargeBinary)
    last_seen: Mapped[Optional[datetime]] = mapped_column()
    
    warranty_expire_date: Mapped[Optional[date]] = mapped_column(Date)
    warranty_provider_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("vendors.id"))
    
    com_port: Mapped[Optional[str]] = mapped_column(String(20))
    dock_serial: Mapped[Optional[str]] = mapped_column(String(100))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    invalid_serial: Mapped[bool] = mapped_column(Boolean, default=False)


class DeviceComponent(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "device_components"

    device_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("devices.id"))
    component_type: Mapped[Optional[str]] = mapped_column(String(50))
    serial_number: Mapped[Optional[str]] = mapped_column(String(100))
    model: Mapped[Optional[str]] = mapped_column(String(100))
    manufacturer: Mapped[Optional[str]] = mapped_column(String(100))
    specifications: Mapped[Optional[dict]] = mapped_column(JSONB)
    slot_name: Mapped[Optional[str]] = mapped_column(String(50))
    is_internal: Mapped[Optional[bool]] = mapped_column(Boolean)
    installation_date: Mapped[Optional[date]] = mapped_column(Date)
    removed_date: Mapped[Optional[date]] = mapped_column(Date)
    status: Mapped[Optional[str]] = mapped_column(String(20))


class DeviceConnection(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "device_connections"

    source_device_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("devices.id"), nullable=False)
    target_device_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("devices.id"), nullable=False)
    connection_type: Mapped[Optional[str]] = mapped_column(String(30))
    port_name: Mapped[Optional[str]] = mapped_column(String(50))
    baud_rate: Mapped[Optional[int]] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    connected_at: Mapped[Optional[datetime]] = mapped_column()
    disconnected_at: Mapped[Optional[datetime]] = mapped_column()


class CMDBRelationship(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "cmdb_relationships"
    __table_args__ = (CheckConstraint('source_id != target_id', name='chk_no_self_relation'),)

    source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("devices.id"), nullable=False)
    target_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("devices.id"), nullable=False)
    relationship_type: Mapped[Optional[str]] = mapped_column(String(50))
