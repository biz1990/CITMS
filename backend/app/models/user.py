import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Text, Boolean, SmallInteger, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, UUIDMixin, TimestampMixin, SoftDeleteMixin

class Role(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    users: Mapped[List["UserRole"]] = relationship(back_populates="role", cascade="all, delete-orphan")
    permissions: Mapped[List["RolePermission"]] = relationship(back_populates="role", cascade="all, delete-orphan")


class UserRole(Base, UUIDMixin):
    __tablename__ = "user_roles"
    __table_args__ = (UniqueConstraint('user_id', 'role_id', name='uq_user_role'),)

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    assigned_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    assigned_by: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id"))

    user: Mapped["User"] = relationship(back_populates="roles", foreign_keys=[user_id])
    role: Mapped["Role"] = relationship(back_populates="users")
    assigner: Mapped[Optional["User"]] = relationship(foreign_keys=[assigned_by])


class Permission(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "permissions"

    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    roles: Mapped[List["RolePermission"]] = relationship(back_populates="permission", cascade="all, delete-orphan")


class RolePermission(Base, UUIDMixin):
    __tablename__ = "role_permissions"
    __table_args__ = (UniqueConstraint('role_id', 'permission_id', name='uq_role_permission'),)

    role_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    permission_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False)

    role: Mapped["Role"] = relationship(back_populates="permissions")
    permission: Mapped["Permission"] = relationship(back_populates="roles")


class User(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[Optional[str]] = mapped_column(String(255))
    full_name: Mapped[Optional[str]] = mapped_column(String(100))
    employee_id: Mapped[Optional[str]] = mapped_column(String(20), unique=True)
    department_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("departments.id"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_login: Mapped[Optional[datetime]] = mapped_column()
    auth_provider: Mapped[str] = mapped_column(String(20), default="LOCAL") 
    preferences: Mapped[dict] = mapped_column(JSONB, default=dict)

    roles: Mapped[List["UserRole"]] = relationship(back_populates="user", foreign_keys="UserRole.user_id", cascade="all, delete-orphan")
    department: Mapped[Optional["Department"]] = relationship(back_populates="users", foreign_keys=[department_id])


class Department(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "departments"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("departments.id"))
    manager_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id")) # Deferred schema in alembic
    level: Mapped[Optional[int]] = mapped_column(SmallInteger)

    users: Mapped[List["User"]] = relationship(back_populates="department", foreign_keys="User.department_id")
    parent: Mapped[Optional["Department"]] = relationship(remote_side="Department.id", backref="sub_departments")
    manager: Mapped[Optional["User"]] = relationship(foreign_keys=[manager_id])
