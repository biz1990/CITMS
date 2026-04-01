from celery import shared_task
from app.core.async_runner import run_async
from app.api.deps import AsyncSessionLocal
from app.services.notification import NotificationService
import uuid

async def _send_notification(user_id: str, title: str, message: str, type_cat: str):
    async with AsyncSessionLocal() as db:
        svc = NotificationService(db)
        await svc.push_notification(uuid.UUID(user_id), title, message, type_cat)
        # Mocking SMTP Email / Websocket Dispatch
        print(f"[CELERY-MAIL] Sending Email to USR:{user_id} - {title}: {message}")
        print(f"[CELERY-WS] Broadcasting Websocket EVENT: {type_cat}")

@shared_task(name="notifications.send_notification_task")
def send_notification_task(user_id: str, title: str, message: str, type_cat: str = "INFO"):
    """ Fire-and-forget notification handling (called via standard code) """
    return run_async(_send_notification(user_id, title, message, type_cat))
