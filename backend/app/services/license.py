import uuid
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.software import SoftwareLicense, SoftwareBlacklist, SoftwareInstallation
from app.core.events import publisher

logger = logging.getLogger(__name__)

class LicenseService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def assign_license(self, installation: SoftwareInstallation):
        """
        Module 9: Link license_id based on software_name and update used_seats.
        This gets called when a new Software is detected during Inventory Ingestion.
        """
        stmt = select(SoftwareLicense).where(SoftwareLicense.software_name == installation.software_name)
        license_obj = (await self.db.execute(stmt)).scalars().first()
        
        if license_obj:
            installation.license_id = license_obj.id
            license_obj.used_seats += 1
            self.db.add(license_obj)
            self.db.add(installation)
            await self.db.flush()
            
            # Check violation immediately (Seats > Total) -> Pub/Sub
            await self.check_compliance(license_obj.id)
        
        # Check blacklist -> Pub/Sub
        is_bad = await self.is_blacklisted(installation.software_name)
        if is_bad:
            installation.is_blocked = True
            await publisher.publish(
                "LICENSE_ALERTS",
                {
                    "event": "BLACKLISTED_SOFTWARE_DETECTED",
                    "device_id": str(installation.device_id),
                    "software": installation.software_name
                }
            )

    async def check_compliance(self, license_id: uuid.UUID) -> bool:
        stmt = select(SoftwareLicense).where(SoftwareLicense.id == license_id)
        license_obj = (await self.db.execute(stmt)).scalars().first()
        
        if not license_obj:
            return True
            
        if license_obj.used_seats > license_obj.total_seats:
            excess = license_obj.used_seats - license_obj.total_seats
            logger.warning(f"License Violation! {license_obj.software_name} by {excess} seats.")
            
            await publisher.publish(
                "LICENSE_ALERTS",
                {
                    "event": "LICENSE_VIOLATED",
                    "license_id": str(license_obj.id),
                    "software": license_obj.software_name,
                    "excess": excess
                }
            )
            return False
            
        return True

    async def is_blacklisted(self, software_name: str) -> bool:
        stmt = select(SoftwareBlacklist).where(SoftwareBlacklist.software_name.ilike(f"%{software_name}%"))
        obj = (await self.db.execute(stmt)).scalars().first()
        return obj is not None
