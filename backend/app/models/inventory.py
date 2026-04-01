import uuid
from typing import Optional
from sqlalchemy import String, Text, SmallInteger, CheckConstraint, Integer, DECIMAL, ForeignKey, Computed
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, UUIDMixin, TimestampMixin, SoftDeleteMixin

class Vendor(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "vendors"
    __table_args__ = (CheckConstraint('rating BETWEEN 1 AND 5', name='chk_vendor_rating'),)

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    contact_person: Mapped[Optional[str]] = mapped_column(String(100))
    email: Mapped[Optional[str]] = mapped_column(String(100))
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    address: Mapped[Optional[str]] = mapped_column(Text)
    contract_details: Mapped[Optional[dict]] = mapped_column(JSONB)
    rating: Mapped[Optional[int]] = mapped_column(SmallInteger)


class SparePartInventory(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "spare_parts_inventory"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    part_number: Mapped[Optional[str]] = mapped_column(String(50))
    category: Mapped[Optional[str]] = mapped_column(String(30))
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    min_quantity: Mapped[int] = mapped_column(Integer, default=5)
    unit_cost: Mapped[Optional[float]] = mapped_column(DECIMAL(12, 2))
    total_value: Mapped[Optional[float]] = mapped_column(
        DECIMAL(12, 2), 
        Computed("quantity * unit_cost", persisted=True)
    )
    location_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("locations.id"))
    vendor_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("vendors.id"))
    image_url: Mapped[Optional[str]] = mapped_column(String(500))
