import uuid
from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import String, Integer, DECIMAL, ForeignKey, Date
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, UUIDMixin, TimestampMixin, SoftDeleteMixin, OptimisticLockMixin

class PurchaseOrder(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin, OptimisticLockMixin):
    __tablename__ = "purchase_orders"

    po_code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(30), default='DRAFT')
    requested_by: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id"))
    approved_by: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id"))
    total_estimated_cost: Mapped[Optional[float]] = mapped_column(DECIMAL(12, 2))
    approved_at: Mapped[Optional[datetime]] = mapped_column()


class PurchaseItem(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "purchase_items"

    purchase_order_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("purchase_orders.id"))
    item_name: Mapped[Optional[str]] = mapped_column(String(100))
    category: Mapped[Optional[str]] = mapped_column(String(30))
    quantity: Mapped[Optional[int]] = mapped_column(Integer)
    unit_price: Mapped[Optional[float]] = mapped_column(DECIMAL(12, 2))
    specifications: Mapped[Optional[dict]] = mapped_column(JSONB)
    received_quantity: Mapped[int] = mapped_column(Integer, default=0)
    received_by: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id"))
    received_at: Mapped[Optional[datetime]] = mapped_column()


class Contract(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "contracts"

    contract_code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    vendor_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("vendors.id"))
    contract_type: Mapped[Optional[str]] = mapped_column(String(30))
    start_date: Mapped[Optional[date]] = mapped_column(Date)
    expire_date: Mapped[Optional[date]] = mapped_column(Date)
    terms: Mapped[Optional[dict]] = mapped_column(JSONB)
