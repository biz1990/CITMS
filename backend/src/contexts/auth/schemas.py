from typing import Optional, List, Any, Dict
from pydantic import BaseModel, EmailStr, Field, validator
from uuid import UUID
from datetime import datetime

class PermissionBase(BaseModel):
    code: str
    name: str
    module: str
    description: Optional[str] = None

class PermissionResponse(PermissionBase):
    id: UUID
    class Config:
        from_attributes = True

class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None

class RoleResponse(RoleBase):
    id: UUID
    permissions: List[PermissionResponse] = []
    class Config:
        from_attributes = True

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    employee_id: Optional[str] = None
    department_id: Optional[UUID] = None
    is_active: bool = True

class UserResponse(UserBase):
    id: UUID
    roles: List[str] = []
    permissions: List[str] = []
    last_login: Optional[datetime] = None
    class Config:
        from_attributes = True

class AuditLogResponse(BaseModel):
    id: UUID
    user_id: Optional[UUID]
    user_name: Optional[str]
    action: str
    resource_type: str
    resource_id: Optional[str]
    status: str
    description: Optional[str]
    old_value: Optional[Dict[str, Any]]
    new_value: Optional[Dict[str, Any]]
    ip_address: Optional[str]
    created_at: datetime
    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    username: str
    password: str
    provider: str = "LOCAL" # LOCAL, LDAP, SSO

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=12)

    @validator('new_password')
    def password_complexity(cls, v):
        if not any(c.isupper() for c in v): raise ValueError('Must contain at least one uppercase letter')
        if not any(c.islower() for c in v): raise ValueError('Must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v): raise ValueError('Must contain at least one digit')
        return v

class SuperUserCreate(BaseModel):
    username: str = Field(..., min_length=3)
    email: EmailStr
    full_name: str
    password: str = Field(..., min_length=12)

    @validator('password')
    def password_complexity(cls, v):
        if not any(c.isupper() for c in v): raise ValueError('Must contain at least one uppercase letter')
        if not any(c.islower() for c in v): raise ValueError('Must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v): raise ValueError('Must contain at least one digit')
        return v
