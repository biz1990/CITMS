import uuid
from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db
from app.api.auth_deps import RequireRole
from app.schemas.workflow import WorkflowRequestCreate, WorkflowRequestResponse
from app.schemas.base import Pagination
from app.models.workflow import WorkflowRequest
from app.services.workflow import WorkflowService

router = APIRouter()

@router.post("/onboarding", response_model=WorkflowRequestResponse)
async def initiate_onboarding(
    *,
    db: AsyncSession = Depends(get_db),
    req_in: WorkflowRequestCreate,
    current_user = Depends(RequireRole("tickets:create"))
) -> Any:
    req = WorkflowRequest(
        workflow_type="ONBOARDING",
        status="PENDING",
        created_by=current_user.id,
        target_user_id=req_in.target_user_id,
        template_details=req_in.template_details
    )
    db.add(req)
    await db.commit()
    await db.refresh(req)
    
    # Auto-execute immediately for demo purposes
    svc = WorkflowService(db)
    await svc.execute_onboarding(req.id)
    await db.refresh(req)
    return req

@router.post("/offboarding/{target_user_id}")
async def initiate_offboarding(
    target_user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(RequireRole("tickets:admin"))
) -> Any:
    svc = WorkflowService(db)
    recovered_count = await svc.execute_offboarding(target_user_id)
    return {"message": "Offboarding executed", "devices_recovered": recovered_count}
