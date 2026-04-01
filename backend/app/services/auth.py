from uuid import UUID
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.core.security import verify_password

class AuthService:
    # Logic RBAC Matrix mapped directly from Module 6
    RBAC_MATRIX = {
        "SUPER_ADMIN": ["users:write", "devices:write", "tickets:admin", "procurement:approve", "license:write", "settings:write"],
        "IT_MANAGER": ["users:read", "devices:write", "tickets:admin", "procurement:approve", "license:write", "settings:read"],
        "IT_STAFF": ["users:read", "devices:update", "tickets:write", "procurement:read", "license:read"],
        "HR_STAFF": ["users:read", "devices:read", "tickets:create", "procurement:create"],
        "REGULAR_USER": ["users:self", "devices:self", "tickets:self"]
    }

    def __init__(self, db: AsyncSession):
        self.db = db

    async def authenticate(self, username: str, password: str) -> Optional[User]:
        stmt = select(User).where(User.username == username, User.is_active == True, User.deleted_at.is_(None))
        result = await self.db.execute(stmt)
        user = result.scalars().first()
        
        if not user or not user.password_hash:
            return None
            
        if not verify_password(password, str(user.password_hash)):
            return None
            
        # Update last login
        from datetime import datetime
        user.last_login = datetime.utcnow()
        await self.db.commit()
            
        return user

    async def ldap_sync(self) -> dict:
        """ Module 6: LDAP Sync Placeholder """
        return {"status": "success", "synced_users": 0}

    async def get_user_permissions(self, user_id: UUID) -> List[str]:
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        user = result.scalars().first()
        
        if not user:
            return []
            
        roles = [r.role.name for r in getattr(user, "roles", [])]
        permissions = set()
        for r in roles:
            for p in self.RBAC_MATRIX.get(r, []):
                permissions.add(p)
                
        # Super admin fallback
        if "SUPER_ADMIN" in roles:
            permissions.update(self.RBAC_MATRIX["SUPER_ADMIN"])
            
        return list(permissions)

    async def check_rbac(self, user_id: UUID, required_permission: str) -> bool:
        permissions = await self.get_user_permissions(user_id)
        return required_permission in permissions
