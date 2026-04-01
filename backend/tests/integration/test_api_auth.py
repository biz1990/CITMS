import pytest
from app.models.user import User
from app.core.security import get_password_hash
import uuid

@pytest.fixture
async def user_db_mock(db_session):
    u = User(id=uuid.uuid4(), username="apiuser", email="api@corp.com", hashed_password=get_password_hash("pass123"), is_active=True)
    db_session.add(u)
    await db_session.commit()
    return u

@pytest.mark.asyncio
async def test_api_login_success(client, user_db_mock):
    response = await client.post("/api/v1/auth/login", data={"username": "apiuser", "password": "pass123"})
    assert response.status_code == 200
    assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_api_login_invalid_credentials(client, user_db_mock):
    response = await client.post("/api/v1/auth/login", data={"username": "apiuser", "password": "wrongpassword"})
    assert response.status_code == 400
    assert response.json()["type"] == "https://citms.internal/errors/invalid-credentials"

@pytest.mark.asyncio
async def test_api_read_me_unauthorized(client):
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401
