import pytest
import uuid
from datetime import datetime
from app.services.itsm import ITSMService
from app.models.ticket import Ticket
from fastapi import HTTPException

@pytest.mark.asyncio
async def test_state_machine_happy_path(db_session):
    svc = ITSMService(db_session)
    t = Ticket(id=uuid.uuid4(), title="Test", description="Test", ticket_code="T-1", status="OPEN", priority="MEDIUM", category="HW", created_by=uuid.uuid4(), version=1)
    db_session.add(t)
    await db_session.commit()
    
    # Valid flow OPEN -> IN_PROGRESS
    res = await svc.advance_state(t.id, "IN_PROGRESS")
    assert res is True
    
    # Assert DB State updated
    await db_session.refresh(t)
    assert t.status == "IN_PROGRESS"

@pytest.mark.asyncio
async def test_state_machine_negative_transition(db_session):
    svc = ITSMService(db_session)
    t = Ticket(id=uuid.uuid4(), title="Test", description="Test", ticket_code="T-2", status="IN_PROGRESS", priority="MEDIUM", category="HW", created_by=uuid.uuid4(), version=1)
    db_session.add(t)
    await db_session.commit()
    
    # Invalid flow IN_PROGRESS -> OPEN
    with pytest.raises(ValueError) as exc:
        await svc.advance_state(t.id, "OPEN")
    
    assert "Invalid internal state transition" in str(exc.value)
    
@pytest.mark.asyncio
async def test_sla_escalation_rules(db_session, monkeypatch):
    svc = ITSMService(db_session)
    
    # Needs escalation - Created way back in the past
    past_date = datetime(2025, 1, 1, 9, 0, 0)
    t = Ticket(id=uuid.uuid4(), title="Test SLA", description="Test", ticket_code="T-3", status="OPEN", priority="MEDIUM", category="HW", created_by=uuid.uuid4(), sla_response_due=past_date, version=1)
    db_session.add(t)
    await db_session.commit()
    
    # Mocking datetime inside ITSMService check to simulate we are past the SLA
    import app.services.itsm
    class MockDatetime:
        @classmethod
        def utcnow(cls):
            return datetime(2025, 1, 2, 9, 0, 0) # Next day!
            
    monkeypatch.setattr(app.services.itsm, 'datetime', MockDatetime)
    
    # Mock Notification
    notified = []
    async def mock_push(*args, **kwargs):
        notified.append(True)
    svc.notification_service.push_notification = mock_push
    
    # Run Escalation Sweep
    await svc.check_escalation_rules()
    
    await db_session.refresh(t)
    # If the logic escalates MEDIUM -> HIGH after SLA breach
    assert t.priority == "HIGH" 
    assert len(notified) > 0 # Escalation must warn managers
