import uuid
from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db
from app.api.auth_deps import RequireRole
from app.schemas.inventory import SparePartCreate, SparePartUpdate, SparePartResponse
from app.schemas.base import Pagination
from app.models.inventory import SparePartInventory

router = APIRouter()

@router.get("/spare-parts", response_model=Pagination[SparePartResponse])
async def read_spare_parts(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(RequireRole("inventory:read"))
) -> Any:
    stmt = select(SparePartInventory).offset(skip).limit(limit)
    parts = (await db.execute(stmt)).scalars().all()
    
    stmt_count = select(SparePartInventory)
    total = len((await db.execute(stmt_count)).scalars().all())
    
    return {
        "items": parts, "total": total, "page": (skip//limit)+1, "size": limit, "has_next": (skip+limit) < total
    }

@router.post("/spare-parts", response_model=SparePartResponse)
async def create_spare_part(
    *,
    db: AsyncSession = Depends(get_db),
    part_in: SparePartCreate,
    current_user = Depends(RequireRole("inventory:write"))
) -> Any:
    part = SparePartInventory(**part_in.model_dump())
    db.add(part)
    await db.commit()
    await db.refresh(part)
    return part
