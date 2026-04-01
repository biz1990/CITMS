import pytest
import uuid
from app.services.notification import NotificationService
from app.models.workflow import Notification

@pytest.mark.asyncio
async def test_notification_push_and_persistence(db_session):
    svc = NotificationService(db_session)
    user_id = uuid.uuid4()
    await svc.push_notification(user_id, "SLA Warning", "Your ticket has 1 hour left", "WARNING")
    
    from sqlalchemy import select
    notif = (await db_session.execute(select(Notification).where(Notification.target_user_id==user_id))).scalars().first()
    assert notif is not None
    assert notif.title == "SLA Warning"
    assert notif.is_read is False

@pytest.mark.asyncio
async def test_notification_mark_read(db_session):
    svc = NotificationService(db_session)
    user_id = uuid.uuid4()
    notif = Notification(id=uuid.uuid4(), target_user_id=user_id, title="Test", message="Test", type="INFO")
    db_session.add(notif)
    await db_session.commit()
    
    await svc.mark_as_read(notif.id)
    await db_session.refresh(notif)
    assert notif.is_read is True
