import uuid
import logging
from datetime import datetime
from typing import Optional, List

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.procurement import PurchaseOrder, PurchaseItem
from app.models.inventory import SparePart, Warehouse
from app.models.workflow import ApprovalHistory, Notification
from app.core.config import settings

logger = logging.getLogger(__name__)

class ProcurementService:
    PO_STATES = {
        "DRAFT": ["PENDING_CAB", "CANCELLED"],
        "PENDING_CAB": ["APPROVED", "REJECTED", "CANCELLED"],
        "APPROVED": ["ORDERED", "CANCELLED"],
        "ORDERED": ["RECEIVED", "PARTIAL_RECEIVED", "CANCELLED"],
        "PARTIAL_RECEIVED": ["RECEIVED", "CANCELLED"],
        "RECEIVED": [],
        "REJECTED": ["DRAFT", "CANCELLED"],
        "CANCELLED": []
    }

    CAB_THRESHOLD = 5000.0  # Module 3.1: PO > $5000 requires CAB

    def __init__(self, db: AsyncSession):
        self.db = db

    async def submit_for_approval(self, po_id: uuid.UUID, user_id: uuid.UUID):
        """Module 3.2: Submit PO to CAB if exceeding threshold"""
        stmt = select(PurchaseOrder).where(PurchaseOrder.id == po_id)
        po = (await self.db.execute(stmt)).scalars().first()
        if not po or po.status != "DRAFT":
            return False
            
        if float(po.total_estimated_cost or 0) >= self.CAB_THRESHOLD:
            po.status = "PENDING_CAB"
            logger.info(f"PO {po.po_code} submitted to CAB for approval.")
        else:
            po.status = "APPROVED"
            po.approved_at = datetime.utcnow()
            po.approved_by = user_id
            logger.info(f"PO {po.po_code} auto-approved (below threshold).")
            
        await self.db.commit()
        return True

    async def approve_po(self, po_id: uuid.UUID, user_id: uuid.UUID, comment: str = ""):
        """Module 3.3: Manual CAB Approval"""
        stmt = select(PurchaseOrder).where(PurchaseOrder.id == po_id)
        po = (await self.db.execute(stmt)).scalars().first()
        if not po or po.status != "PENDING_CAB":
            return False
            
        po.status = "APPROVED"
        po.approved_at = datetime.utcnow()
        po.approved_by = user_id
        
        # Log Approval
        history = ApprovalHistory(
            entity_type="PURCHASE_ORDER",
            entity_id=po_id,
            action="APPROVE",
            user_id=user_id,
            comment=comment
        )
        self.db.add(history)
        await self.db.commit()
        return True

    async def receive_items(self, po_id: uuid.UUID, items_received: List[dict], user_id: uuid.UUID):
        """
        Module 3.4: Finalize PO Receipt.
        Auto-ingest into SparePartsInventory or Devices.
        """
        stmt = select(PurchaseOrder).where(PurchaseOrder.id == po_id).options(selectinload(PurchaseOrder.items))
        po = (await self.db.execute(stmt)).scalars().first()
        if not po or po.status not in ["ORDERED", "PARTIAL_RECEIVED"]:
            return False
            
        for r_item in items_received:
            # Update PurchaseItem quantity
            p_item_stmt = select(PurchaseItem).where(PurchaseItem.id == r_item["item_id"])
            p_item = (await self.db.execute(p_item_stmt)).scalars().first()
            if p_item:
                p_item.received_quantity += r_item["quantity"]
                p_item.received_by = user_id
                p_item.received_at = datetime.utcnow()
                
                # Module 4: Auto-ingest into Spare Parts
                # We assume category matches the inventory types
                new_spare = SparePart(
                    name=p_item.item_name,
                    category=p_item.category,
                    quantity=r_item["quantity"],
                    unit_cost=p_item.unit_price,
                    po_id=po_id
                )
                self.db.add(new_spare)

        # Check if fully received
        po.status = "RECEIVED"
        await self.db.commit()
        return True
