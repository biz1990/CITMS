from typing import Optional, List, Any
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
from backend.src.infrastructure.repositories.base import BaseRepository
from backend.src.contexts.auth.models import User, Role, Permission, AuditLog
import uuid

class AuditLogRepository(BaseRepository[AuditLog]):
    def __init__(self, db):
        super().__init__(AuditLog, db)

    async def list_logs(self, limit: int = 100) -> List[dict]:
        query = select(AuditLog).options(selectinload(AuditLog.user)).order_by(AuditLog.created_at.desc()).limit(limit)
        result = await self.db.execute(query)
        logs = result.scalars().all()
        
        return [
            {
                "id": log.id,
                "user_id": log.user_id,
                "user_name": log.user.full_name if log.user else "System",
                "action": log.action,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "status": log.status,
                "description": log.details.get("description") if log.details else None,
                "old_value": log.details.get("old_data") if log.details else None,
                "new_value": log.details.get("new_data") if log.details else None,
                "ip_address": log.ip_address,
                "created_at": log.created_at
            } for log in logs
        ]

class UserRepository(BaseRepository[User]):
    def __init__(self, db):
        super().__init__(User, db)

    async def get_by_username(self, username: str) -> Optional[User]:
        query = select(User).where(
            and_(User.username == username, User.deleted_at == None)
        ).options(
            selectinload(User.roles).selectinload(Role.permissions)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        query = select(User).where(
            and_(User.email == email, User.deleted_at == None)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_user_with_permissions(self, user_id: uuid.UUID) -> Optional[User]:
        query = select(User).where(
            and_(User.id == user_id, User.deleted_at == None)
        ).options(
            selectinload(User.roles).selectinload(Role.permissions)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

class RoleRepository(BaseRepository[Role]):
    def __init__(self, db):
        super().__init__(Role, db)

    async def get_by_name(self, name: str) -> Optional[Role]:
        query = select(Role).where(
            and_(Role.name == name, Role.deleted_at == None)
        ).options(selectinload(Role.permissions))
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

class PermissionRepository(BaseRepository[Permission]):
    def __init__(self, db):
        super().__init__(Permission, db)

    async def get_by_code(self, code: str) -> Optional[Permission]:
        query = select(Permission).where(
            and_(Permission.code == code, Permission.deleted_at == None)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
