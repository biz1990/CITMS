from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any

from app.main import limiter

from app.api.deps import get_db # From phase 0
from app.api.auth_deps import get_current_user, get_current_active_user, RequireRole
from app.services.auth import AuthService
from app.core.security import create_access_token
from app.schemas.user import Token, UserResponse, UserCreate
from app.core.exceptions import CITMSException

router = APIRouter()

@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
async def login_access_token(
    request: Request,
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    auth_service = AuthService(db)
    user = await auth_service.authenticate(
        username=form_data.username, password=form_data.password
    )
    if not user:
        raise CITMSException(status_code=400, title="Login Failed", detail="Incorrect username or password", error_type="invalid-credentials")
    
    # Optional logic to fetch Roles and map them to UserResponse structure
    roles = [r.role.name for r in getattr(user, "roles", [])]
        
    return {
        "access_token": create_access_token(user.id),
        "refresh_token": "placeholder-refresh-token",
        "expires_in": 3600,
        "user": {
            **user.__dict__,
            "roles": roles
        }
    }

@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    roles = [r.role.name for r in getattr(current_user, "roles", [])]
    return {**current_user.__dict__, "roles": roles}

@router.post("/ldap-sync")
async def sync_ldap(
    current_user = Depends(RequireRole("users:write")),
    db: AsyncSession = Depends(get_db)
) -> Any:
    auth_service = AuthService(db)
    result = await auth_service.ldap_sync()
    return result
