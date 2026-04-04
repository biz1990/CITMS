import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.schemas.inventory_survey import (
    InventorySurveyCreate,
    InventorySurveyResponse,
    SurveyItemResponse,
    ScanSubmit
)
from app.services.inventory_survey import InventorySurveyService
from app.core.auth import RequireRole

router = APIRouter()

@router.post("/", response_model=InventorySurveyResponse, dependencies=[Depends(RequireRole("inventory:write"))])
async def create_survey(
    obj_in: InventorySurveyCreate,
    db: AsyncSession = Depends(deps.get_db)
):
    svc = InventorySurveyService(db)
    return await svc.create_survey(name=obj_in.name, location_id=obj_in.location_id)

@router.get("/", response_model=List[InventorySurveyResponse], dependencies=[Depends(RequireRole("inventory:read"))])
async def get_surveys(
    db: AsyncSession = Depends(deps.get_db)
):
    from sqlalchemy import select
    from app.models.inventory_survey import InventorySurvey
    stmt = select(InventorySurvey).where(InventorySurvey.deleted_at.is_(None)).order_by(InventorySurvey.created_at.desc())
    results = (await db.execute(stmt)).scalars().all()
    return results

@router.post("/{survey_id}/scan", response_model=SurveyItemResponse, dependencies=[Depends(RequireRole("inventory:write"))])
async def submit_scan(
    survey_id: uuid.UUID,
    obj_in: ScanSubmit,
    db: AsyncSession = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_user)
):
    svc = InventorySurveyService(db)
    return await svc.submit_scan(
        survey_id=survey_id,
        asset_tag=obj_in.asset_tag,
        actual_location_id=obj_in.actual_location_id,
        user_id=current_user.id
    )

@router.post("/{survey_id}/reconcile", dependencies=[Depends(RequireRole("inventory:write"))])
async def reconcile_survey(
    survey_id: uuid.UUID,
    db: AsyncSession = Depends(deps.get_db)
):
    svc = InventorySurveyService(db)
    success = await svc.reconcile_survey(survey_id)
    if not success:
        raise HTTPException(status_code=400, detail="Cannot reconcile this survey. It may be closed already or non-existent.")
    return {"status": "success", "message": "Assets reconciled and survey closed."}
