import uuid
import httpx
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.cache import cache
from app.models.device import Device
from app.core.exceptions import CITMSException

class RustDeskService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_remote_session(self, device_id: uuid.UUID) -> dict:
        """
        v3.6 §13.2: Remote Control RustDesk Zero-Password Flow.
        1. Fetch rustdesk_id.
        2. Request temp token from RustDesk Server.
        3. Store in Redis with 300s TTL.
        """
        # 1. Fetch rustdesk_id
        stmt = select(Device.rustdesk_id).where(Device.id == device_id)
        rustdesk_id = (await self.db.execute(stmt)).scalars().first()
        
        if not rustdesk_id:
            raise CITMSException(
                status_code=404, 
                title="RustDesk ID Not Found", 
                detail="Thiết bị này chưa được cấu hình RustDesk ID.",
                error_type="not-found"
            )

        # 2. Request temp session from RustDesk Server
        # Simulation of enterprise API call as per §13.2 diagram
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # v3.6 §13.2 calls POST /api/temporary/session
                response = await client.post(
                    f"{settings.RUSTDESK_API_URL}/api/temporary/session",
                    json={"rustdesk_id": rustdesk_id},
                    headers={"Authorization": f"Bearer {settings.RUSTDESK_API_TOKEN}"}
                )
                
                if response.status_code != 200:
                    # Fallback for dev/mock if server not reachable, 
                    # but in production this must hit the real server.
                    if settings.ENVIRONMENT == "development":
                        temp_token = f"dev_token_{uuid.uuid4().hex[:12]}"
                    else:
                        raise CITMSException(
                            status_code=502,
                            title="RustDesk Server Error",
                            detail="Không thể khởi tạo phiên làm việc với RustDesk server.",
                            error_type="service-unavailable"
                        )
                else:
                    data = response.json()
                    temp_token = data.get("temporary_session_token")
        except httpx.RequestError:
            if settings.ENVIRONMENT == "development":
                temp_token = f"dev_token_{uuid.uuid4().hex[:12]}"
            else:
                raise CITMSException(
                    status_code=502,
                    title="Network Error",
                    detail="Lỗi mạng khi kết nối tới RustDesk server.",
                    error_type="service-unavailable"
                )

        # 3. Store in Redis (300s TTL as per §13.2)
        redis_key = f"rustdesk:session:{device_id}"
        expiry_at = datetime.utcnow() + timedelta(seconds=300)
        
        await cache.set(redis_key, {"token": temp_token}, ttl=300)

        return {
            "rustdesk_id": rustdesk_id,
            "temporary_session_token": temp_token,
            "expires_at": expiry_at
        }
