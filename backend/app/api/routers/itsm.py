import uuid
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.api.auth_deps import RequireRole
from app.schemas.itsm import TicketCreate, TicketUpdate, TicketResponse
from app.schemas.base import Pagination
from app.crud.crud_ticket import ticket as crud_ticket
from app.services.itsm import ITSMService

router = APIRouter()

@router.get("/", response_model=Pagination[TicketResponse])
async def read_tickets(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(RequireRole("tickets:read")) # Extrapolated read role
) -> Any:
    tickets = await crud_ticket.get_multi(db, skip=skip, limit=limit)
    return {
        "items": tickets, "total": 0, "page": 1, "size": limit, "has_next": False # dummy counts
    }

@router.post("/", response_model=TicketResponse)
async def create_ticket(
    *,
    db: AsyncSession = Depends(get_db),
    ticket_in: TicketCreate,
    current_user = Depends(RequireRole("tickets:create"))
) -> Any:
    return await crud_ticket.create(db=db, obj_in=ticket_in)

@router.put("/{id}/state")
async def update_ticket_state(
    id: uuid.UUID,
    new_state: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(RequireRole("tickets:write"))
) -> Any:
    svc = ITSMService(db)
    try:
        success = await svc.advance_state(id, new_state)
        if not success:
            raise HTTPException(status_code=404, detail="Ticket not found")
        return {"message": "State advanced successfully"}
    except ValueError as e:
        from app.core.exceptions import CITMSException
        raise CITMSException(status_code=400, title="Bad Request", detail=str(e), error_type="invalid-state-transition")
