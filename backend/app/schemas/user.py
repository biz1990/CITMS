import uuid
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, EmailStr

# Role Schemas
class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None

class RoleResponse(RoleBase):
    id: uuid.UUID
    
    model_config = ConfigDict(from_attributes=True)

# User Schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    employee_id: Optional[str] = None
    is_active: bool = True
    auth_provider: str = "LOCAL"

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    preferences: Optional[dict] = None

class UserInDB(UserBase):
    id: uuid.UUID
    department_id: Optional[uuid.UUID] = None
    preferences: dict = {}
    
    model_config = ConfigDict(from_attributes=True)

class UserResponse(UserInDB):
    roles: List[str] = [] # Flattened role names

# Token Schemas
class Token(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    user: UserResponse

class TokenPayload(BaseModel):
    sub: Optional[str] = None
