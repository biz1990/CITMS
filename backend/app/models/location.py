import uuid
from typing import Optional
from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, UUIDMixin, TimestampMixin, SoftDeleteMixin

class Location(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "locations"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("locations.id"))
    location_code: Mapped[Optional[str]] = mapped_column(String(20), unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    parent: Mapped[Optional["Location"]] = relationship(remote_side="Location.id", backref="sub_locations")
