import uuid
from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.api.auth_deps import RequireRole

router = APIRouter()

@router.post("/escalation-check", status_code=202)
async def run_escalation_checks(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(RequireRole("admin:system"))
) -> Any:
    """Cron-triggered endpoint for SLA and escalation parsing."""
    from app.services.itsm import ITSMService
    svc = ITSMService(db)
    await svc.check_escalation_rules()
    return {"message": "Escalation rules executed"}
