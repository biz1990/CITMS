import pytest
from app.models.user import User, Role, UserRole
import uuid
from app.core.security import create_access_token

@pytest.fixture
async def valid_token_devices_read(db_session):
    # Mocking a user with device:read permission
    u = User(id=uuid.uuid4(), username="reader", email="r@r.com", hashed_password="pw", is_active=True)
    r = Role(id=uuid.uuid4(), name="DEV_READER", permissions={"devices:read": True})
    ur = UserRole(user_id=u.id, role_id=r.id)
    db_session.add_all([u, r, ur])
    await db_session.commit()
    return create_access_token(u.id)

@pytest.mark.asyncio
async def test_api_get_devices_pagination(client, valid_token_devices_read):
    headers = {"Authorization": f"Bearer {valid_token_devices_read}"}
    response = await client.get("/api/v1/devices/?skip=0&limit=10", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data

@pytest.mark.asyncio
async def test_api_create_device_forbidden(client, valid_token_devices_read):
    # Token only has devices:read, but POST requires devices:write
    headers = {"Authorization": f"Bearer {valid_token_devices_read}"}
    payload = {"serial_number": "SN-1", "device_type": "LAPTOP"}
    response = await client.post("/api/v1/devices/", json=payload, headers=headers)
    assert response.status_code == 403
    assert response.json()["type"] == "https://citms.internal/errors/forbidden"
