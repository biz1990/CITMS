from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from backend.src.infrastructure.database import get_db
from backend.src.contexts.procurement.schemas import (
    POCreate, POResponse, POStatusUpdate, 
    ReceiveItemRequest, VendorBase, VendorResponse
)
from backend.src.contexts.procurement.services import ProcurementService
from backend.src.contexts.procurement.models import PurchaseOrder, Vendor
from backend.src.infrastructure.dependencies.pagination import PaginationParams, get_pagination_params
from backend.src.contexts.auth.dependencies import get_current_user, PermissionChecker
from backend.src.contexts.auth.models import User
from sqlalchemy import select

router = APIRouter(prefix="/procurement", tags=["Procurement & Warehouse"])

@router.get("/purchase-orders", response_model=List[POResponse])
async def list_pos(
    pagination: PaginationParams = Depends(get_pagination_params),
    status: Optional[str] = None,
    vendor_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _ = Depends(PermissionChecker(["po.view"]))
):
    query = select(PurchaseOrder)
    if status:
        query = query.where(PurchaseOrder.status == status)
    if vendor_id:
        query = query.where(PurchaseOrder.vendor_id == vendor_id)
    query = query.order_by(PurchaseOrder.created_at.desc()).offset(pagination.skip).limit(pagination.limit)
    res = await db.execute(query)
    return res.scalars().all()

@router.post("/purchase-orders", response_model=POResponse)
async def create_po(
    po_in: POCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _ = Depends(PermissionChecker(["po.create"]))
):
    service = ProcurementService(db)
    data = po_in.dict()
    items = data.pop("items")
    data["requested_by"] = current_user.id
    return await service.create_po(data, items)

@router.patch("/purchase-orders/{id}/status", response_model=POResponse)
async def update_po_status(
    id: UUID,
    status_in: POStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _ = Depends(PermissionChecker(["po.approve"]))
):
    service = ProcurementService(db)
    return await service.update_po_status(id, status_in.status, current_user.id)

@router.post("/purchase-orders/{id}/receive-items", status_code=status.HTTP_200_OK)
async def receive_items(
    id: UUID,
    receive_in: ReceiveItemRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _ = Depends(PermissionChecker(["po.receive"]))
):
    service = ProcurementService(db)
    await service.receive_items(id, receive_in.item_id, receive_in.quantity)
    return {"status": "success"}

# Vendor CRUD
@router.get("/vendors", response_model=List[VendorResponse])
async def list_vendors(
    pagination: PaginationParams = Depends(get_pagination_params),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(select(Vendor).offset(pagination.skip).limit(pagination.limit))
    return res.scalars().all()

@router.post("/vendors", response_model=VendorResponse)
async def create_vendor(vendor_in: VendorBase, db: AsyncSession = Depends(get_db)):
    vendor = Vendor(**vendor_in.dict())
    db.add(vendor)
    await db.commit()
    await db.refresh(vendor)
    return vendor
