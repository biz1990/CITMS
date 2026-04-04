import uuid
from typing import Any, List
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db # from phase 0
from app.api.auth_deps import get_current_active_user, RequireRole
from app.schemas.device import DeviceCreate, DeviceUpdate, DeviceResponse, ReconcileRequest
from app.schemas.base import Pagination
from app.crud.crud_device import device as crud_device
from app.models.device import Device
from app.services.inventory_ingestion import InventoryIngestionService
from app.services.asset import AssetService
from app.core.exceptions import CITMSException

router = APIRouter()

@router.get("/", response_model=Pagination[DeviceResponse])
async def read_devices(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(RequireRole("devices:read"))
) -> Any:
    devices = await crud_device.get_multi(db, skip=skip, limit=limit)
    # Get total count (simplistic)
    stmt = select(Device).where(Device.deleted_at.is_(None))
    total = len((await db.execute(stmt)).scalars().all())
    
    return {
        "items": devices,
        "total": total,
        "page": (skip // limit) + 1,
        "size": limit,
        "has_next": (skip + limit) < total
    }

@router.post("/", response_model=DeviceResponse)
async def create_device(
    *,
    db: AsyncSession = Depends(get_db),
    device_in: DeviceCreate,
    current_user = Depends(RequireRole("devices:write"))
) -> Any:
    # Use repo pattern
    return await crud_device.create(db=db, obj_in=device_in)

@router.post("/reconcile")
async def reconcile_inventory(
    *,
    db: AsyncSession = Depends(get_db),
    req: ReconcileRequest,
    current_user = Depends(RequireRole("devices:write"))
) -> Any:
    # Heavy business logic from Phase 2
    svc = InventoryIngestionService(db)
    await svc.process_report(req.run_id, req.model_dump())
    return {"message": "Reconciliation completed successfully", "run_id": req.run_id}

@router.get("/{id}/topology")
async def get_device_topology(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(RequireRole("devices:read"))
) -> Any:
    svc = AssetService(db)
    graph = await svc.build_topology_graph(id)
    return graph

@router.post("/{id}/remote-session", response_model=RemoteSessionResponse)
async def create_remote_session(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(RequireRole("devices:remote"))
) -> Any:
    """v3.6 §5.1, §13.2: Initiates a zero-password remote control session."""
    from app.services.rustdesk import RustDeskService
    svc = RustDeskService(db)
    return await svc.create_remote_session(id)
