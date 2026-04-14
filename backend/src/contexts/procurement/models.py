from sqlalchemy import String, ForeignKey, DateTime, Boolean, Integer, Numeric, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.src.infrastructure.models.base import CITMSBaseModel
from typing import Optional, List
from datetime import datetime
import uuid
import enum

class POStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    RECEIVING = "RECEIVING"
    COMPLETED = "COMPLETED"

class Vendor(CITMSBaseModel):
    __tablename__ = "vendors"
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    contact_person: Mapped[Optional[str]] = mapped_column(String(100))
    email: Mapped[Optional[str]] = mapped_column(String(100))
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    address: Mapped[Optional[str]] = mapped_column(String)
    tax_code: Mapped[Optional[str]] = mapped_column(String(50))

class Contract(CITMSBaseModel):
    __tablename__ = "contracts"
    contract_number: Mapped[str] = mapped_column(String(50), unique=True)
    vendor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("vendors.id"))
    start_date: Mapped[datetime] = mapped_column(DateTime)
    end_date: Mapped[datetime] = mapped_column(DateTime)
    total_value: Mapped[float] = mapped_column(Numeric(15, 2))
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE")

class SparePart(CITMSBaseModel):
    __tablename__ = "spare_parts"
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(String(50))
    manufacturer: Mapped[Optional[str]] = mapped_column(String(100))
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    min_quantity: Mapped[int] = mapped_column(Integer, default=5)
    unit_price: Mapped[float] = mapped_column(Numeric(15, 2), default=0)

class PurchaseOrder(CITMSBaseModel):
    __tablename__ = "purchase_orders"
    po_number: Mapped[str] = mapped_column(String(50), unique=True)
    vendor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("vendors.id"))
    status: Mapped[POStatus] = mapped_column(String(30), default=POStatus.DRAFT)
    total_amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    requested_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    approved_by: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id"))
    version: Mapped[int] = mapped_column(Integer, default=1)
    
    items: Mapped[List["PurchaseItem"]] = relationship(back_populates="po", cascade="all, delete-orphan")

class PurchaseItem(CITMSBaseModel):
    __tablename__ = "purchase_items"
    po_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("purchase_orders.id"))
    spare_part_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("spare_parts.id"))
    item_name: Mapped[str] = mapped_column(String(200))
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price: Mapped[float] = mapped_column(Numeric(15, 2))
    received_quantity: Mapped[int] = mapped_column(Integer, default=0)
    
    po: Mapped["PurchaseOrder"] = relationship(back_populates="items")
    spare_part: Mapped[Optional["SparePart"]] = relationship()
