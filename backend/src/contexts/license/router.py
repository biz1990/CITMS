from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from backend.src.infrastructure.database import get_db
from backend.src.contexts.license.schemas import LicenseCreate, LicenseResponse, ViolationCheckResponse
from backend.src.contexts.license.repositories import LicenseRepository
from backend.src.contexts.license.services.license import LicenseService
from backend.src.contexts.auth.dependencies import get_current_user, PermissionChecker
from backend.src.contexts.auth.models import User

router = APIRouter(prefix="/licenses", tags=["License & Compliance"])

@router.get("/", response_model=List[LicenseResponse])
async def list_licenses(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _ = Depends(PermissionChecker(["license.view"]))
):
    repo = LicenseRepository(db)
    return await repo.get_all()

@router.post("/", response_model=LicenseResponse)
async def create_license(
    license_in: LicenseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _ = Depends(PermissionChecker(["license.create"]))
):
    repo = LicenseRepository(db)
    # In real app, encrypt license_key here
    return await repo.create(license_in.dict())

@router.get("/check-violations", response_model=ViolationCheckResponse)
async def check_violations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _ = Depends(PermissionChecker(["license.view"]))
):
    repo = LicenseRepository(db)
    violations = await repo.list_violations()
    
    return ViolationCheckResponse(
        violated_licenses=[LicenseResponse.from_orm(v) for v in violations],
        blacklisted_software_detected=[], # In real app, fetch from logs
        blacklisted_serials_detected=[]
    )
