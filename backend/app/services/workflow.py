import uuid
import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.workflow import DeviceAssignment, WorkflowRequest
from app.models.device import Device
from app.models.inventory import SparePartInventory

logger = logging.getLogger(__name__)

class WorkflowService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def execute_onboarding(self, workflow_request_id: uuid.UUID) -> bool:
        """
        Module 10: Onboarding -> read template -> deduct spare_parts -> create assignment
        """
        stmt = select(WorkflowRequest).where(WorkflowRequest.id == workflow_request_id)
        req = (await self.db.execute(stmt)).scalars().first()
        
        if not req or req.status == "COMPLETED":
            return False
            
        template = req.template_details or {}
        required_parts = template.get("required_parts", [])
        
        # Deduct inventory
        for part in required_parts:
            stmt_part = select(SparePartInventory).where(SparePartInventory.part_number == part["part_number"])
            inv_part = (await self.db.execute(stmt_part)).scalars().first()
            if inv_part and inv_part.quantity >= part["qty"]:
                inv_part.quantity -= part["qty"]
            else:
                logger.error(f"Not enough inventory for {part['part_number']} during onboarding.")
                
        # Assign existing reserved device if requested
        reserved_device_id = template.get("assigned_device_id")
        if reserved_device_id:
            asn = DeviceAssignment(
                device_id=uuid.UUID(reserved_device_id),
                user_id=req.target_user_id,
                assignment_type="PERMANENT",
                assigned_at=datetime.utcnow()
            )
            self.db.add(asn)
            
            stmt_dev = select(Device).where(Device.id == uuid.UUID(reserved_device_id))
            dev = (await self.db.execute(stmt_dev)).scalars().first()
            if dev:
                dev.status = "IN_USE"
                dev.version += 1
            
        req.status = "COMPLETED"
        req.completed_at = datetime.utcnow()
        await self.db.commit()
        return True
        
    async def execute_offboarding(self, target_user_id: uuid.UUID) -> int:
        """
        Module 10: Offboarding workflow (Return assigned devices and set conditions to IN_STOCK/PENDING)
        """
        stmt = select(DeviceAssignment).where(
            DeviceAssignment.user_id == target_user_id, 
            DeviceAssignment.returned_at.is_(None)
        )
        assignments = (await self.db.execute(stmt)).scalars().all()
        
        for asn in assignments:
            asn.returned_at = datetime.utcnow()
            asn.return_condition = "PENDING_CHECK"
            
            stmt_dev = select(Device).where(Device.id == asn.device_id)
            dev = (await self.db.execute(stmt_dev)).scalars().first()
            if dev:
                dev.status = "IN_STOCK"
                dev.version += 1
                
        await self.db.commit()
        return len(assignments)
