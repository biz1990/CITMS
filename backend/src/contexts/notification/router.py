from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID
from backend.src.infrastructure.database import get_db
from backend.src.contexts.notification.schemas import NotificationResponse, MarkReadRequest
from backend.src.contexts.notification.models import Notification
from backend.src.contexts.notification.services.websocket import ws_manager
from backend.src.contexts.auth.dependencies import get_current_user, PermissionChecker
from backend.src.contexts.auth.models import User
from sqlalchemy import select, update

router = APIRouter(prefix="/notifications", tags=["Notification Engine"])

@router.get("/", response_model=List[NotificationResponse])
async def list_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _ = Depends(PermissionChecker(["notification.view"]))
):
    res = await db.execute(
        select(Notification)
        .where(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
        .limit(50)
    )
    return res.scalars().all()

@router.patch("/{id}/read", status_code=status.HTTP_200_OK)
async def mark_as_read(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await db.execute(
        update(Notification)
        .where(and_(Notification.id == id, Notification.user_id == current_user.id))
        .values(is_read=True)
    )
    await db.commit()
    return {"status": "marked_as_read"}

@router.post("/mark-all-read", status_code=status.HTTP_200_OK)
async def mark_all_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await db.execute(
        update(Notification)
        .where(Notification.user_id == current_user.id)
        .values(is_read=True)
    )
    await db.commit()
    return {"status": "all_marked_as_read"}

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for realtime notifications."""
    # In production, verify token here
    await ws_manager.connect(websocket, user_id)
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            # Handle client-side messages if needed
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, user_id)
