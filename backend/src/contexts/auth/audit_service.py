from typing import Optional, Any, Dict
from datetime import datetime
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.contexts.auth.models import AuditLog

class AuditService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def log(
        self,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        user_id: Optional[uuid.UUID] = None,
        status: str = "SUCCESS",
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None
    ):
        """
        Creates an audit log entry.
        """
        audit_entry = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            status=status,
            details=details,
            ip_address=ip_address,
            created_at=datetime.utcnow()
        )
        self.db.add(audit_entry)
        await self.db.commit()
        return audit_entry
