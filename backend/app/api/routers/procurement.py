import uuid
from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db
from app.api.auth_deps import RequireRole
from app.schemas.procurement import PurchaseOrderCreate, PurchaseOrderUpdate, PurchaseOrderResponse
from app.schemas.base import Pagination
from app.models.procurement import PurchaseOrder

router = APIRouter()

@router.get("/", response_model=Pagination[PurchaseOrderResponse])
async def read_purchase_orders(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(RequireRole("procurement:read"))
) -> Any:
    stmt = select(PurchaseOrder).offset(skip).limit(limit)
    pos = (await db.execute(stmt)).scalars().all()
    
    total = len((await db.execute(select(PurchaseOrder))).scalars().all())
    return {
        "items": pos, "total": total, "page": (skip//limit)+1, "size": limit, "has_next": (skip+limit)<total
    }

@router.post("/", response_model=PurchaseOrderResponse)
async def create_purchase_order(
    *,
    db: AsyncSession = Depends(get_db),
    po_in: PurchaseOrderCreate,
    current_user = Depends(RequireRole("procurement:write"))
) -> Any:
    po = PurchaseOrder(
        **po_in.model_dump(),
        po_number=f"PO-{uuid.uuid4().hex[:8].upper()}",
        created_by=current_user.id
    )
    db.add(po)
    await db.commit()
    await db.refresh(po)
    return po
