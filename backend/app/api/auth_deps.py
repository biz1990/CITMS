from typing import AsyncGenerator
from collections.abc import AsyncGenerator as AbcAsyncGenerator
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.api.deps import get_db # from phase 0
from app.models.user import User
from app.services.auth import AuthService
from app.core.exceptions import CITMSException

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)

async def get_current_user(
    db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=["HS256"]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise CITMSException(status_code=401, title="Unauthorized", detail="Invalid token payload", error_type="unauthorized")
    except JWTError:
        raise CITMSException(status_code=401, title="Unauthorized", detail="Could not validate credentials", error_type="unauthorized")
        
    stmt = select(User).where(User.id == user_id)
    user = (await db.execute(stmt)).scalars().first()
    if not user:
        raise CITMSException(status_code=404, title="User Not Found", detail="User not found", error_type="not-found")
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise CITMSException(status_code=403, title="Forbidden", detail="Inactive user", error_type="forbidden")
    return current_user

class RequireRole:
    def __init__(self, required_permission: str):
        self.required_permission = required_permission

    async def __call__(self, current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
        auth_service = AuthService(db)
        has_permission = await auth_service.check_rbac(current_user.id, self.required_permission)
        if not has_permission:
            raise CITMSException(
                status_code=403, 
                title="Quyền truy cập bị từ chối", 
                detail=f"Tài khoản không có quyền: {self.required_permission}", 
                error_type="forbidden"
            )
        return current_user
