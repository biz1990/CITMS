import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.workflow import Notification

class NotificationService:
    # 12 Core Alert Types from Module 7
    ALERT_TYPES = [
        "AGENT_OFFLINE", 
        "PARTS_UNAUTHORIZED_MOVE", 
        "BLACKLISTED_SOFTWARE",
        "LICENSE_EXPIRE_SOON", 
        "LOW_INVENTORY", 
        "CLONED_SERIAL",
        "SLA_BREACH", 
        "RECALL_FAILED", 
        "DISPOSAL_PENDING", 
        "WARRANTY_EXPIRE", 
        "RECONCILE_NEEDED", 
        "LICENSE_VIOLATION"
    ]

    def __init__(self, db: AsyncSession):
        self.db = db

    async def push_notification(self, user_id: uuid.UUID, title: str, message: str, type_cat: str = "INFO", channel: str = "SYSTEM_WS") -> Notification:
        # Pushes to DB. Realtime WS server fetches from this table.
        notif = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=type_cat,
            channel=channel
        )
        self.db.add(notif)
        await self.db.commit()
        return notif
