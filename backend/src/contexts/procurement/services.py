from datetime import datetime
from typing import List, Optional, Any
from uuid import UUID
from sqlalchemy import select, and_, update
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.contexts.procurement.models import PurchaseOrder, POStatus, PurchaseItem, SparePart
from fastapi import HTTPException

class ProcurementService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_po(self, data: dict, items: List[dict]) -> PurchaseOrder:
        """Create a new PO in DRAFT state."""
        po = PurchaseOrder(**data)
        po.status = POStatus.DRAFT
        
        # Calculate total amount
        total = 0
        for item in items:
            total += item["quantity"] * item["unit_price"]
            po.items.append(PurchaseItem(**item))
        
        po.total_amount = total
        self.db.add(po)
        await self.db.commit()
        await self.db.refresh(po)
        return po

    async def update_po_status(self, po_id: UUID, new_status: POStatus, user_id: UUID) -> PurchaseOrder:
        """Handle PO state transitions."""
        res = await self.db.execute(select(PurchaseOrder).where(PurchaseOrder.id == po_id))
        po = res.scalar_one_or_none()
        if not po:
            raise HTTPException(status_code=404, detail="PO not found")

        # State Machine Logic
        valid_transitions = {
            POStatus.DRAFT: [POStatus.PENDING_APPROVAL],
            POStatus.PENDING_APPROVAL: [POStatus.APPROVED, POStatus.REJECTED],
            POStatus.APPROVED: [POStatus.RECEIVING],
            POStatus.RECEIVING: [POStatus.COMPLETED],
            POStatus.REJECTED: [POStatus.DRAFT],
            POStatus.COMPLETED: []
        }

        if new_status not in valid_transitions.get(po.status, []):
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid transition from {po.status} to {new_status}"
            )

        if new_status == POStatus.APPROVED:
            po.approved_by = user_id
        
        po.status = new_status
        await self.db.commit()
        await self.db.refresh(po)
        return po

    async def receive_items(self, po_id: UUID, item_id: UUID, quantity: int):
        """Receive items for a PO in RECEIVING state and update SparePart inventory."""
        res = await self.db.execute(select(PurchaseOrder).where(PurchaseOrder.id == po_id))
        po = res.scalar_one_or_none()
        if not po or po.status != POStatus.RECEIVING:
            raise HTTPException(status_code=400, detail="PO must be in RECEIVING state")

        res = await self.db.execute(select(PurchaseItem).where(PurchaseItem.id == item_id))
        item = res.scalar_one_or_none()
        if not item or item.po_id != po_id:
            raise HTTPException(status_code=404, detail="Item not found in this PO")

        item.received_quantity += quantity
        if item.received_quantity > item.quantity:
            raise HTTPException(status_code=400, detail="Received quantity exceeds ordered quantity")

        # Update SparePart Inventory if linked
        if item.spare_part_id:
            res = await self.db.execute(select(SparePart).where(SparePart.id == item.spare_part_id))
            part = res.scalar_one_or_none()
            if part:
                part.quantity += quantity
                # Check for low stock alert
                if part.quantity < part.min_quantity:
                    from backend.src.contexts.notification.services.event_bus import EventPublisher, EventType
                    await EventPublisher.publish(EventType.SPARE_PARTS_BELOW_MIN, part.id, {
                        "name": part.name,
                        "quantity": part.quantity,
                        "min_quantity": part.min_quantity
                    })

        await self.db.commit()
        
        # Auto-complete PO if all items received
        all_received = all(i.received_quantity == i.quantity for i in po.items)
        if all_received:
            po.status = POStatus.COMPLETED
            await self.db.commit()
