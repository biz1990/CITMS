import asyncio
import sys
import os

# Add the project root to sys.path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from sqlalchemy import select
from backend.src.infrastructure.database import AsyncSessionLocal
from backend.src.contexts.auth.models import User, Role, Permission, RolePermission
from backend.src.core.security import get_password_hash

# Default Permissions for CITMS 3.6
DEFAULT_PERMISSIONS = [
    {"code": "dashboard.view", "name": "View Dashboard", "module": "Dashboard"},
    {"code": "asset.view", "name": "View Assets", "module": "Asset"},
    {"code": "asset.create", "name": "Create Assets", "module": "Asset"},
    {"code": "asset.edit", "name": "Edit Assets", "module": "Asset"},
    {"code": "asset.delete", "name": "Delete Assets", "module": "Asset"},
    {"code": "user.view", "name": "View Users", "module": "User"},
    {"code": "user.manage", "name": "Manage Users", "module": "User"},
    {"code": "role.view", "name": "View Roles", "module": "RBAC"},
    {"code": "role.manage", "name": "Manage Roles", "module": "RBAC"},
    {"code": "audit.view", "name": "View Audit Logs", "module": "Audit"},
    {"code": "license.view", "name": "View Licenses", "module": "License"},
    {"code": "license.manage", "name": "Manage Licenses", "module": "License"},
    {"code": "procurement.view", "name": "View Procurement", "module": "Procurement"},
    {"code": "procurement.approve", "name": "Approve Procurement", "module": "Procurement"},
    {"code": "workflow.view", "name": "View Workflows", "module": "Workflow"},
    {"code": "workflow.approve", "name": "Approve Workflows", "module": "Workflow"},
    {"code": "remote.control", "name": "Remote Control Access", "module": "Remote"},
    {"code": "settings.manage", "name": "Manage System Settings", "module": "Settings"},
]

# Default Roles
DEFAULT_ROLES = [
    {"name": "SUPER_ADMIN", "description": "Full system access"},
    {"name": "IT_MANAGER", "description": "IT Management access"},
    {"name": "IT_STAFF", "description": "IT Operations access"},
    {"name": "DEPARTMENT_HEAD", "description": "Departmental approval access"},
    {"name": "REGULAR_USER", "description": "Basic self-service access"},
]

async def init_system():
    async with AsyncSessionLocal() as session:
        # 1. Seed Permissions
        print("Seeding permissions...")
        for perm_data in DEFAULT_PERMISSIONS:
            stmt = select(Permission).where(Permission.code == perm_data["code"])
            result = await session.execute(stmt)
            if not result.scalar_one_or_none():
                perm = Permission(**perm_data)
                session.add(perm)
        
        await session.commit()

        # 2. Seed Roles
        print("Seeding roles...")
        roles_map = {}
        for role_data in DEFAULT_ROLES:
            stmt = select(Role).where(Role.name == role_data["name"])
            result = await session.execute(stmt)
            role = result.scalar_one_or_none()
            if not role:
                role = Role(**role_data)
                session.add(role)
                await session.flush()
            else:
                # Update description if needed
                role.description = role_data["description"]
            roles_map[role.name] = role
        
        await session.commit()

        # 3. Assign all permissions to SUPER_ADMIN
        print("Assigning permissions to SUPER_ADMIN...")
        super_admin_role = roles_map["SUPER_ADMIN"]
        stmt = select(Permission)
        result = await session.execute(stmt)
        all_permissions = result.scalars().all()
        
        # Load existing permissions to avoid duplicates in the relationship
        stmt = select(Role).where(Role.id == super_admin_role.id).options(
            # We need to load permissions to check
            # But since it's a script, we can just clear and re-add or check
            # For simplicity, let's just check if it's already there
        )
        # Actually, SQLAlchemy relationship handling will manage duplicates if we use a set or check
        
        current_perm_ids = [p.id for p in super_admin_role.permissions]
        for perm in all_permissions:
            if perm.id not in current_perm_ids:
                super_admin_role.permissions.append(perm)
        
        await session.commit()
        print("System initialization complete.")

async def create_superuser(username, email, full_name, password):
    async with AsyncSessionLocal() as session:
        # Check if any user exists
        stmt = select(User)
        result = await session.execute(stmt)
        if result.first():
            print("Error: A user already exists. Superuser creation is disabled for security.")
            return

        # Get SUPER_ADMIN role
        stmt = select(Role).where(Role.name == "SUPER_ADMIN")
        result = await session.execute(stmt)
        super_admin_role = result.scalar_one_or_none()
        
        if not super_admin_role:
            print("Error: SUPER_ADMIN role not found. Run init_system first.")
            return

        # Create user
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            password_hash=get_password_hash(password),
            is_active=True
        )
        user.roles.append(super_admin_role)
        session.add(user)
        await session.commit()
        print(f"Superuser '{username}' created successfully.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python init_system.py [init|create-superuser]")
        sys.exit(1)
    
    command = sys.argv[1]
    if command == "init":
        asyncio.run(init_system())
    elif command == "create-superuser":
        if len(sys.argv) != 6:
            print("Usage: python init_system.py create-superuser <username> <email> <full_name> <password>")
            sys.exit(1)
        asyncio.run(create_superuser(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]))
    else:
        print(f"Unknown command: {command}")
