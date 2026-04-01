import pytest
import uuid
from app.services.auth import AuthService
from app.models.user import User, Role, UserRole

@pytest.mark.asyncio
async def test_password_hashing(db_session):
    svc = AuthService(db_session)
    hashed = svc.get_password_hash("SecretData123!")
    assert hashed != "SecretData123!"
    assert svc.verify_password("SecretData123!", hashed) is True
    assert svc.verify_password("wrongpass", hashed) is False

@pytest.mark.asyncio
async def test_rbac_check_success(db_session):
    u = User(id=uuid.uuid4(), username="admin", email="admin@corp.com", hashed_password="pw", is_active=True)
    r = Role(id=uuid.uuid4(), name="SUPER_ADMIN", description="All perm", permissions={"*" : True})
    ur = UserRole(user_id=u.id, role_id=r.id)
    
    db_session.add_all([u, r, ur])
    await db_session.commit()
    
    svc = AuthService(db_session)
    # Simulate DB fetching the role logic (already verified via Mock DB mapping previously in auth.py)
    # We directly test checking the matrix.
    res = await svc.check_rbac(u.id, "devices:write")
    assert res is True  # Super admin should bypass or naturally pass based on auth logic

@pytest.mark.asyncio
async def test_rbac_check_forbidden(db_session):
    u = User(id=uuid.uuid4(), username="viewer", email="v@corp.com", hashed_password="pw", is_active=True)
    r = Role(id=uuid.uuid4(), name="VIEWER", description="Limited", permissions={"devices:read" : True})
    ur = UserRole(user_id=u.id, role_id=r.id)
    
    db_session.add_all([u, r, ur])
    await db_session.commit()
    
    svc = AuthService(db_session)
    res = await svc.check_rbac(u.id, "devices:write")
    assert res is False

@pytest.mark.asyncio
async def test_ldap_sync_trigger(db_session):
    svc = AuthService(db_session)
    result = await svc.ldap_sync()
    assert result == {"synced_users": 0} # Empty DB / mocked LDAP returns 0 sync initially
