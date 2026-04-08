from __future__ import annotations
from sqlalchemy import select, String, JSON
from sqlalchemy.orm import Mapped, mapped_column
from backend.src.infrastructure.models.base import CITMSBaseModel
from backend.src.infrastructure.repositories.base import BaseRepository
from typing import Any, Optional
import uuid

class SystemSetting(CITMSBaseModel):
    __tablename__ = "system_settings"
    
    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[Any] = mapped_column(JSON, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    updated_by: Mapped[Optional[uuid.UUID]] = mapped_column(nullable=True)

class SettingsRepository(BaseRepository[SystemSetting]):
    async def get_by_key(self, key: str) -> Optional[SystemSetting]:
        query = select(SystemSetting).where(SystemSetting.key == key)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
