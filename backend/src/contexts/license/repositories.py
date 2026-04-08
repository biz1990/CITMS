from typing import Optional, List, Any
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
from backend.src.infrastructure.repositories.base import BaseRepository
from backend.src.contexts.license.models import SoftwareLicense, SerialBlacklist, SoftwareBlacklist
import uuid

class LicenseRepository(BaseRepository[SoftwareLicense]):
    def __init__(self, db):
        super().__init__(SoftwareLicense, db)

    async def get_available_license(self, catalog_id: uuid.UUID) -> Optional[SoftwareLicense]:
        """Find a license for a specific software that still has seats."""
        query = select(SoftwareLicense).where(
            and_(
                SoftwareLicense.software_catalog_id == catalog_id,
                SoftwareLicense.used_seats < SoftwareLicense.total_seats,
                SoftwareLicense.deleted_at == None
            )
        ).order_by(SoftwareLicense.expire_date.asc()).with_for_update() # Use license expiring soonest with pessimistic lock
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def assign_license(self, license_id: uuid.UUID) -> bool:
        """Increment used_seats for a license with pessimistic locking."""
        query = select(SoftwareLicense).where(
            SoftwareLicense.id == license_id
        ).with_for_update()
        
        result = await self.db.execute(query)
        license = result.scalar_one_or_none()
        
        if license and license.used_seats < license.total_seats:
            license.used_seats += 1
            return True
        return False

    async def list_violations(self) -> List[SoftwareLicense]:
        """Find all licenses where used_seats > total_seats."""
        query = select(SoftwareLicense).where(
            and_(
                SoftwareLicense.used_seats > SoftwareLicense.total_seats,
                SoftwareLicense.deleted_at == None
            )
        )
        result = await self.db.execute(query)
        return result.scalars().all()

class BlacklistRepository:
    def __init__(self, db):
        self.db = db

    async def get_serial_blacklist(self, serial: str) -> Optional[SerialBlacklist]:
        query = select(SerialBlacklist).where(SerialBlacklist.serial_number == serial)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_software_blacklist(self, name: str) -> Optional[SoftwareBlacklist]:
        query = select(SoftwareBlacklist).where(SoftwareBlacklist.software_name == name)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
