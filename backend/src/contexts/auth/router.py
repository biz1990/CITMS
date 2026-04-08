from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.infrastructure.database import get_db
from backend.src.contexts.auth.schemas import (
    LoginRequest, TokenResponse, UserResponse, 
    RefreshTokenRequest, PasswordChangeRequest,
    RoleResponse, PermissionResponse, AuditLogResponse,
    SuperUserCreate
)
from backend.src.contexts.auth.repositories import UserRepository, RoleRepository, PermissionRepository, AuditLogRepository
from backend.src.contexts.auth.services import AuthService
from backend.src.contexts.auth.dependencies import get_current_user, PermissionChecker
from backend.src.contexts.auth.models import User, Role
from backend.src.core.security import get_password_hash
from sqlalchemy import select
import uuid

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    user_repo = UserRepository(db)
    auth_service = AuthService(user_repo)
    return await auth_service.authenticate(login_data)

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    user_roles = [role.name for role in current_user.roles]
    user_permissions = list(set([p.code for role in current_user.roles for p in role.permissions]))
    
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        employee_id=current_user.employee_id,
        department_id=current_user.department_id,
        is_active=current_user.is_active,
        roles=user_roles,
        permissions=user_permissions,
        last_login=current_user.last_login
    )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    # Logic to decode refresh token and issue new access token
    # For simplicity, we'll assume it's valid if it decodes
    from jose import jwt, JWTError
    from backend.src.core.config import settings
    from backend.src.core.security import create_access_token, create_refresh_token
    
    try:
        payload = jwt.decode(refresh_data.refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
        
    user_repo = UserRepository(db)
    user = await user_repo.get_user_with_permissions(uuid.UUID(user_id))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
        
    user_roles = [role.name for role in user.roles]
    user_permissions = list(set([p.code for role in user.roles for p in role.permissions]))
    
    user_resp = UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        employee_id=user.employee_id,
        department_id=user.department_id,
        is_active=user.is_active,
        roles=user_roles,
        permissions=user_permissions,
        last_login=user.last_login
    )

    return TokenResponse(
        access_token=create_access_token(data={"sub": str(user.id)}),
        refresh_token=create_refresh_token(data={"sub": str(user.id)}),
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user_resp
    )

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    # In a real app, we might blacklist the token in Redis
    return {"message": "Successfully logged out"}

@router.post("/ldap-sync")
async def ldap_sync(
    current_user: User = Depends(get_current_user),
    _ = Depends(PermissionChecker("USER_SYNC"))
):
    # Mock LDAP Sync logic
    return {"message": "LDAP sync completed successfully", "synced_users": 10}

# Role & Permission CRUD (Simplified)
@router.get("/roles", response_model=list[RoleResponse])
async def list_roles(
    db: AsyncSession = Depends(get_db),
    _ = Depends(PermissionChecker("ROLE_VIEW"))
):
    role_repo = RoleRepository(db)
    return await role_repo.list()

@router.get("/permissions", response_model=list[PermissionResponse])
async def list_permissions(
    db: AsyncSession = Depends(get_db),
    _ = Depends(PermissionChecker("PERMISSION_VIEW"))
):
    perm_repo = PermissionRepository(db)
    return await perm_repo.list()

@router.get("/audit-logs", response_model=list[AuditLogResponse])
async def list_audit_logs(
    db: AsyncSession = Depends(get_db),
    _ = Depends(PermissionChecker("AUDIT_VIEW"))
):
    repo = AuditLogRepository(db)
    return await repo.list_logs()

# User CRUD
@router.get("/users", response_model=list[UserResponse])
async def list_users(
    db: AsyncSession = Depends(get_db),
    _ = Depends(PermissionChecker("USER_VIEW"))
):
    user_repo = UserRepository(db)
    users = await user_repo.list()
    
    # Map to include role names
    res = []
    for user in users:
        user_roles = [role.name for role in user.roles]
        res.append(UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            employee_id=user.employee_id,
            department_id=user.department_id,
            is_active=user.is_active,
            roles=user_roles,
            last_login=user.last_login
        ))
    return res

@router.patch("/users/{id}", response_model=UserResponse)
async def update_user(
    id: uuid.UUID,
    user_data: dict,
    db: AsyncSession = Depends(get_db),
    _ = Depends(PermissionChecker("USER_EDIT"))
):
    user_repo = UserRepository(db)
    user = await user_repo.get(id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    for key, value in user_data.items():
        if hasattr(user, key):
            setattr(user, key, value)
            
    await db.commit()
    await db.refresh(user)
    
    user_roles = [role.name for role in user.roles]
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        employee_id=user.employee_id,
        department_id=user.department_id,
        is_active=user.is_active,
        roles=user_roles,
        last_login=user.last_login
    )

@router.delete("/users/{id}")
async def delete_user(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _ = Depends(PermissionChecker("USER_DELETE"))
):
    user_repo = UserRepository(db)
    await user_repo.delete(id)
    return {"status": "deleted"}

@router.post("/init-superuser", response_model=UserResponse)
async def init_superuser(
    user_in: SuperUserCreate,
    db: AsyncSession = Depends(get_db)
):
    # Check if any user exists
    stmt = select(User)
    result = await db.execute(stmt)
    if result.first():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superuser creation is only allowed when no users exist."
        )
    
    # Get SUPER_ADMIN role
    stmt = select(Role).where(Role.name == "SUPER_ADMIN")
    result = await db.execute(stmt)
    super_admin_role = result.scalar_one_or_none()
    
    if not super_admin_role:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SUPER_ADMIN role not found. Please run system initialization first."
        )
    
    # Create user
    user = User(
        username=user_in.username,
        email=user_in.email,
        full_name=user_in.full_name,
        password_hash=get_password_hash(user_in.password),
        is_active=True
    )
    user.roles.append(super_admin_role)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        roles=["SUPER_ADMIN"],
        permissions=list(set([p.code for p in super_admin_role.permissions]))
    )
