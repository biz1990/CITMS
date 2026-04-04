import uuid
import logging
from datetime import datetime
from typing import List, Optional

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.inventory_survey import InventorySurvey, SurveyItem
from app.models.device import Device
from app.models.location import Location

logger = logging.getLogger(__name__)

class InventorySurveyService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_survey(self, name: str, location_id: Optional[uuid.UUID] = None) -> InventorySurvey:
        survey = InventorySurvey(name=name, location_id=location_id)
        self.db.add(survey)
        await self.db.commit()
        await self.db.refresh(survey)
        return survey

    async def submit_scan(self, survey_id: uuid.UUID, asset_tag: str, actual_location_id: uuid.UUID, user_id: uuid.UUID) -> SurveyItem:
        # 1. Lookup device
        stmt = select(Device).where(Device.asset_tag == asset_tag, Device.deleted_at.is_(None))
        device = (await self.db.execute(stmt)).scalars().first()
        
        status = "UNKNOWN"
        expected_location = None
        device_id = None
        
        if device:
            device_id = device.id
            expected_location = device.location_id
            if str(expected_location) == str(actual_location_id):
                status = "MATCHED"
            else:
                status = "MISPLACED"
                
        # 2. Create Survey Item
        item = SurveyItem(
            survey_id=survey_id,
            device_id=device_id,
            asset_tag=asset_tag,
            status=status,
            expected_location_id=expected_location,
            actual_location_id=actual_location_id,
            scanned_by=user_id,
            scanned_at=datetime.utcnow()
        )
        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def reconcile_survey(self, survey_id: uuid.UUID):
        """
        Module 11: Bulk update device locations for MISPLACED items.
        Mark survey as CLOSED/RECONCILED.
        """
        stmt = select(InventorySurvey).where(InventorySurvey.id == survey_id).options(selectinload(InventorySurvey.items))
        survey = (await self.db.execute(stmt)).scalars().first()
        if not survey or survey.status != "OPEN":
            return False
            
        for item in survey.items:
            if item.status == "MISPLACED" and item.device_id:
                # Update device location to actual scanned location
                device_stmt = select(Device).where(Device.id == item.device_id)
                device = (await self.db.execute(device_stmt)).scalars().first()
                if device:
                    device.location_id = item.actual_location_id
                    device.updated_at = datetime.utcnow()
                    # Trigger audit log indirectly (middleware handled)
                    self.db.add(device)
                    
        survey.status = "RECONCILED"
        survey.closed_at = datetime.utcnow()
        self.db.add(survey)
        await self.db.commit()
        return True
