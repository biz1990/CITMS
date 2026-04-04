from uuid import UUID
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.core.security import verify_password

class AuthService:
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
        """v3.6 §3.1: Granular permission retrieval using RolePermission mapping table."""
        from app.models.user import UserRole, Role, RolePermission, Permission

        # Join User -> UserRole -> Role -> RolePermission -> Permission
        stmt = (
            select(Permission.code)
            .join(RolePermission, Permission.id == RolePermission.permission_id)
            .join(Role, RolePermission.role_id == Role.id)
            .join(UserRole, Role.id == UserRole.role_id)
            .where(UserRole.user_id == user_id)
        )
        
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def check_rbac(self, user_id: UUID, required_permission: str) -> bool:
        permissions = await self.get_user_permissions(user_id)
        return required_permission in permissions
