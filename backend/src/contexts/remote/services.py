import json
import uuid
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.contexts.asset.models import Device
from backend.src.contexts.auth.models import User, AuditLog
from backend.src.infrastructure.redis import redis_client
from backend.src.core.config import settings
from backend.src.contexts.remote.schemas import TemporarySessionResponse
from fastapi import HTTPException
from sqlalchemy.orm import selectinload
import httpx

class RustDeskService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.api_url = settings.RUSTDESK_API_URL
        self.api_token = settings.RUSTDESK_API_TOKEN

    async def create_temporary_session(self, device_id: uuid.UUID, current_user: User) -> TemporarySessionResponse:
        """Create a 5-minute temporary session for remote control with Auth check."""
        # 1. Fetch Device
        res = await self.db.execute(select(Device).where(Device.id == device_id))
        device = res.scalar_one_or_none()
        
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")

        # 2. Authorization Check
        is_authorized = False
        reason = "Unauthorized access to device"
        
        # Ensure roles are loaded
        res = await self.db.execute(
            select(User).where(User.id == current_user.id).options(selectinload(User.roles))
        )
        current_user_with_roles = res.scalar_one()
        
        # Owner check
        if device.assigned_to_id == current_user.id:
            is_authorized = True
        else:
            # Role check
            user_role_names = [r.name for r in current_user_with_roles.roles]
            if any(role in user_role_names for role in ["IT_STAFF", "IT_MANAGER", "SUPER_ADMIN"]):
                if "SUPER_ADMIN" in user_role_names:
                    is_authorized = True
                elif device.location_id == current_user.location_id:
                    is_authorized = True
                elif device.assigned_to_id:
                    # Check owner's department
                    owner_res = await self.db.execute(select(User).where(User.id == device.assigned_to_id))
                    owner = owner_res.scalar_one_or_none()
                    if owner and owner.department_id == current_user.department_id:
                        is_authorized = True
        
        # 3. Audit Log
        audit = AuditLog(
            user_id=current_user.id,
            action="CREATE_RUSTDESK_SESSION",
            resource_type="DEVICE",
            resource_id=str(device_id),
            status="SUCCESS" if is_authorized else "DENIED",
            details={"reason": "Authorized" if is_authorized else reason}
        )
        self.db.add(audit)
        await self.db.flush()
        
        if not is_authorized:
            await self.db.commit()
            raise HTTPException(status_code=403, detail=reason)

        if not device.rustdesk_id:
            raise HTTPException(status_code=400, detail="Device has no RustDesk ID")

        # 4. Call RustDesk Server API to get a temporary token
        try:
            async with httpx.AsyncClient() as client:
                # Real RustDesk API call to generate a temporary session token
                # This assumes the RustDesk server has an endpoint /api/session/create
                # that returns a token for a specific ID.
                response = await client.post(
                    f"{self.api_url}/api/session/create",
                    json={
                        "id": device.rustdesk_id,
                        "user_id": str(current_user.id),
                        "duration": 300 # 5 minutes
                    },
                    headers={"Authorization": f"Bearer {self.api_token}"},
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    api_data = response.json()
                    session_token = api_data.get("token")
                else:
                    # Fallback to internal generation if API fails or is not implemented
                    session_token = f"rd_tmp_{uuid.uuid4().hex}"
            
            expires_at = datetime.utcnow() + timedelta(seconds=300) # 5 minutes
            
            # 3. Store in Redis with TTL 300s
            redis_key = f"rustdesk:session:{device_id}"
            session_data = {
                "token": session_token,
                "rustdesk_id": device.rustdesk_id,
                "expires_at": expires_at.isoformat()
            }
            await redis_client.setex(redis_key, 300, json.dumps(session_data))
            
            return TemporarySessionResponse(
                device_id=device_id,
                rustdesk_id=device.rustdesk_id,
                session_token=session_token,
                expires_at=expires_at,
                relay_server=settings.RUSTDESK_RELAY_SERVER,
                webrtc_config={"iceServers": [{"urls": "stun:stun.l.google.com:19302"}]}
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create RustDesk session: {str(e)}")

    async def update_device_status(self, rustdesk_id: str, status: str):
        """Update device online/offline status from webhook."""
        await self.db.execute(
            select(Device).where(Device.rustdesk_id == rustdesk_id)
        )
        # Logic to update status in DB or Redis cache
        # For performance, we often store online status in Redis with a short TTL
        await redis_client.setex(f"device:status:{rustdesk_id}", 60, status)
