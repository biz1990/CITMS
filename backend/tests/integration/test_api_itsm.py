import pytest
import uuid
from app.core.security import create_access_token
from app.models.user import User, Role, UserRole

@pytest.fixture
async def active_token_itsm(db_session):
    u = User(id=uuid.uuid4(), username="itsm_admin", email="t@t.com", hashed_password="pw", is_active=True)
    r = Role(id=uuid.uuid4(), name="ITSM", permissions={"tickets:read": True, "tickets:write": True, "tickets:create": True})
    ur = UserRole(user_id=u.id, role_id=r.id)
    db_session.add_all([u, r, ur])
    await db_session.commit()
    return create_access_token(u.id)

@pytest.mark.asyncio
async def test_api_create_ticket(client, active_token_itsm):
    headers = {"Authorization": f"Bearer {active_token_itsm}"}
    payload = {"title": "Issue", "description": "Details", "category": "HW", "priority": "CRITICAL"}
    response = await client.post("/api/v1/itsm/", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json()["priority"] == "CRITICAL"

@pytest.mark.asyncio
async def test_api_update_ticket_state_not_found(client, active_token_itsm):
    headers = {"Authorization": f"Bearer {active_token_itsm}"}
    fake_id = str(uuid.uuid4())
    # Fails business rule because ticket doc doesn't exist
    response = await client.put(f"/api/v1/itsm/{fake_id}/state?new_state=IN_PROGRESS", headers=headers)
    assert response.status_code == 404
