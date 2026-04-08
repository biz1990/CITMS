from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from backend.src.infrastructure.database import get_db
from backend.src.contexts.remote.schemas import TemporarySessionResponse
from backend.src.contexts.remote.services import RustDeskService
from backend.src.contexts.auth.dependencies import get_current_user, PermissionChecker
from backend.src.contexts.auth.models import User

router = APIRouter(prefix="/devices", tags=["Remote Control"])

@router.post("/{id}/remote-session", response_model=TemporarySessionResponse)
async def create_remote_session(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _ = Depends(PermissionChecker(["remote.control"]))
):
    """Create a temporary session for remote control (Zero-Password)."""
    service = RustDeskService(db)
    return await service.create_temporary_session(id, current_user)
