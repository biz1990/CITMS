import uuid
from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db
from app.api.auth_deps import RequireRole
from app.schemas.inventory import VendorCreate, VendorResponse
from app.schemas.procurement import ContractCreate, ContractResponse
from app.schemas.base import Pagination
from app.models.inventory import Vendor
from app.models.procurement import Contract

router = APIRouter()

@router.get("/", response_model=Pagination[VendorResponse])
async def read_vendors(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(RequireRole("procurement:read"))
) -> Any:
    stmt = select(Vendor).offset(skip).limit(limit)
    items = (await db.execute(stmt)).scalars().all()
    return {"items": items, "total": len(items), "page": 1, "size": limit, "has_next": False}

@router.post("/", response_model=VendorResponse)
async def create_vendor(
    *,
    db: AsyncSession = Depends(get_db),
    vendor_in: VendorCreate,
    current_user = Depends(RequireRole("procurement:write"))
) -> Any:
    vendor = Vendor(**vendor_in.model_dump())
    db.add(vendor)
    await db.commit()
    await db.refresh(vendor)
    return vendor

@router.get("/{id}/contracts", response_model=List[ContractResponse])
async def read_vendor_contracts(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(RequireRole("procurement:read"))
) -> Any:
    stmt = select(Contract).where(Contract.vendor_id == id)
    return (await db.execute(stmt)).scalars().all()

@router.post("/{id}/contracts", response_model=ContractResponse)
async def create_contract(
    id: uuid.UUID,
    contract_in: ContractCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(RequireRole("procurement:write"))
) -> Any:
    contract = Contract(**contract_in.model_dump(), vendor_id=id)
    db.add(contract)
    await db.commit()
    await db.refresh(contract)
    return contract
