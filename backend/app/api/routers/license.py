import uuid
from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db
from app.api.auth_deps import RequireRole
from app.schemas.software import SoftwareLicenseCreate, SoftwareLicenseResponse, ViolationReportResponse
from app.schemas.base import Pagination
from app.models.software import SoftwareLicense
from app.services.license import LicenseService

router = APIRouter()

@router.get("/", response_model=Pagination[SoftwareLicenseResponse])
async def read_licenses(
    db: AsyncSession = Depends(get_db),
    skip: int = 0, limit: int = 100,
    current_user = Depends(RequireRole("license:read"))
) -> Any:
    stmt = select(SoftwareLicense).offset(skip).limit(limit)
    items = (await db.execute(stmt)).scalars().all()
    return {"items": items, "total": len(items), "page": 1, "size": limit, "has_next": False}

@router.post("/", response_model=SoftwareLicenseResponse)
async def create_license(
    *,
    db: AsyncSession = Depends(get_db),
    lic_in: SoftwareLicenseCreate,
    current_user = Depends(RequireRole("license:write"))
) -> Any:
    lic = SoftwareLicense(**lic_in.model_dump())
    db.add(lic)
    await db.commit()
    await db.refresh(lic)
    return lic

@router.get("/violations", response_model=List[ViolationReportResponse])
async def get_violations(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(RequireRole("license:read"))
) -> Any:
    stmt = select(SoftwareLicense).where(SoftwareLicense.used_seats > SoftwareLicense.total_seats)
    violations = (await db.execute(stmt)).scalars().all()
    
    res = []
    for v in violations:
        res.append({
            "software_name": v.software_name,
            "total_seats": v.total_seats,
            "used_seats": v.used_seats,
            "excess": v.used_seats - v.total_seats
        })
    return res
