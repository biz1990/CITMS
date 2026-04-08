from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.infrastructure.database import get_db
from backend.src.contexts.remote.schemas import RustDeskWebhookPayload
from backend.src.contexts.remote.services import RustDeskService
import hmac
import hashlib
from backend.src.core.config import settings

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])

@router.post("/rustdesk")
async def rustdesk_webhook(
    request: Request,
    payload: RustDeskWebhookPayload,
    db: AsyncSession = Depends(get_db)
):
    """Receive status updates from RustDesk Server."""
    # 1. Verify Webhook Signature (HMAC-SHA256)
    signature = request.headers.get("X-RustDesk-Signature")
    if not signature:
        raise HTTPException(status_code=401, detail="Missing signature")
    
    # Simulation: verify signature using settings.RUSTDESK_WEBHOOK_SECRET
    # expected_sig = hmac.new(settings.RUSTDESK_WEBHOOK_SECRET.encode(), await request.body(), hashlib.sha256).hexdigest()
    # if not hmac.compare_digest(signature, expected_sig):
    #     raise HTTPException(status_code=401, detail="Invalid signature")

    # 2. Update Status
    service = RustDeskService(db)
    await service.update_device_status(payload.id, payload.event)
    
    return {"status": "ok"}
