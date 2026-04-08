import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException
from backend.src.contexts.remote.services import RustDeskService
from backend.src.contexts.asset.models import Device
from backend.src.contexts.auth.models import User, Role

@pytest.mark.asyncio
async def test_create_session_unauthorized():
    # Setup
    db = AsyncMock()
    service = RustDeskService(db)
    
    device_id = uuid4()
    user_id = uuid4()
    other_user_id = uuid4()
    
    # Mock Device owned by someone else
    device = Device(id=device_id, assigned_to_id=other_user_id, rustdesk_id="rd123", location_id=uuid4())
    db.execute.return_value.scalar_one_or_none.return_value = device
    
    # Mock Current User (Regular User, not owner)
    current_user = User(id=user_id, roles=[], location_id=uuid4(), department_id=uuid4())
    
    # Mock User with roles loading
    db.execute.return_value.scalar_one.return_value = current_user
    
    # Execute & Assert
    with pytest.raises(HTTPException) as exc:
        await service.create_temporary_session(device_id, current_user)
    
    assert exc.value.status_code == 403
    assert "Unauthorized" in exc.value.detail
    
    # Verify Audit Log was created
    assert db.add.called
    audit = db.add.call_args[0][0]
    assert audit.status == "DENIED"
    assert audit.action == "CREATE_RUSTDESK_SESSION"

@pytest.mark.asyncio
async def test_create_session_authorized_it_staff():
    # Setup
    db = AsyncMock()
    service = RustDeskService(db)
    
    device_id = uuid4()
    user_id = uuid4()
    location_id = uuid4()
    
    # Mock Device in same location
    device = Device(id=device_id, assigned_to_id=uuid4(), rustdesk_id="rd123", location_id=location_id)
    db.execute.return_value.scalar_one_or_none.return_value = device
    
    # Mock IT Staff in same location
    it_role = Role(name="IT_STAFF")
    current_user = User(id=user_id, roles=[it_role], location_id=location_id)
    db.execute.return_value.scalar_one.return_value = current_user
    
    # Execute
    # Should not raise 403
    # Note: It might raise 500 later due to mock RustDesk API call, but auth should pass
    try:
        await service.create_temporary_session(device_id, current_user)
    except HTTPException as e:
        assert e.status_code != 403
