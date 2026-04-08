from datetime import datetime
from typing import Optional, List, Any
from uuid import UUID
from sqlalchemy import select, and_, update
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.contexts.license.models import SoftwareLicense, SoftwareBlacklist
from backend.src.contexts.license.repositories import LicenseRepository, BlacklistRepository
from backend.src.contexts.inventory.services.events import InventoryEventPublisher
from backend.src.contexts.inventory.models import SoftwareInstallation
from fastapi import HTTPException

class LicenseService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.license_repo = LicenseRepository(db)
        self.blacklist_repo = BlacklistRepository(db)

    async def auto_assign_license(self, catalog_id: UUID, installation_id: UUID):
        """Find an available license and assign it to a new installation with pessimistic locking."""
        # 1. Find and lock available license
        license = await self.license_repo.get_available_license(catalog_id)
        
        if license:
            # 2. Increment seat count manually (pessimistic lock is already held)
            # This is safer than relying on triggers alone under high concurrency
            success = await self.license_repo.assign_license(license.id)
            
            if success:
                # 3. Update installation to use this license
                await self.db.execute(
                    update(SoftwareInstallation)
                    .where(SoftwareInstallation.id == installation_id)
                    .values(license_id=license.id)
                )
                await self.db.commit()
                
                # 4. Check for violation after assignment
                await self.db.refresh(license)
                if license.used_seats > license.total_seats:
                    await InventoryEventPublisher.publish_license_violation(
                        license.id, 
                        "Software Name (Catalog ID)", 
                        license.used_seats, 
                        license.total_seats
                    )
            else:
                # No seats left after acquiring lock (unlikely but possible)
                await self.db.rollback()
                raise HTTPException(status_code=400, detail="No available license seats")
        else:
            raise HTTPException(status_code=400, detail="No available license found")

    async def check_software_blacklist(self, software_name: str, device_id: UUID):
        """Check if software is blacklisted and alert if detected."""
        blacklist_entry = await self.blacklist_repo.get_software_blacklist(software_name)
        if blacklist_entry:
            await InventoryEventPublisher.publish("SOFTWARE_BLACKLIST_DETECTED", device_id, {
                "software_name": software_name,
                "reason": blacklist_entry.reason,
                "detected_at": datetime.utcnow().isoformat()
            })
            return True
        return False

    async def check_serial_blacklist(self, serial: str, device_id: UUID):
        """Check if serial number is blacklisted and alert if detected."""
        blacklist_entry = await self.blacklist_repo.get_serial_blacklist(serial)
        if blacklist_entry:
            await InventoryEventPublisher.publish("SERIAL_CLONE_DETECTED", device_id, {
                "serial_number": serial,
                "reason": blacklist_entry.reason,
                "detected_at": datetime.utcnow().isoformat()
            })
            return True
        return False
