import uuid
import logging
import aiosmtplib
from email.message import EmailMessage
from celery import shared_task

from app.core.async_runner import run_async
from app.api.deps import AsyncSessionLocal
from app.services.notification import NotificationService
from app.core.websocket import manager
from app.core.config import settings
from app.models.user import User

logger = logging.getLogger(__name__)

async def _dispatch_notification(user_id_str: str, title: str, message: str, type_cat: str):
    user_id = uuid.UUID(user_id_str)
    
    # 1. Persist to DB
    async with AsyncSessionLocal() as db:
        svc = NotificationService(db)
        await svc.push_notification(user_id, title, message, type_cat)
    
    # 2. Realtime WebSocket Broadcast
    payload = {
        "title": title,
        "message": message,
        "type": type_cat,
        "timestamp": str(uuid.uuid4()) # For React key
    }
    await manager.send_personal_message(payload, user_id)
    logger.info(f"[WS] Dispatched notification to User {user_id}")

    # 3. Email Dispatch (Module 7.1)
    if settings.EMAILS_ENABLED:
        try:
            # Resolve actual user email from DB
            async with AsyncSessionLocal() as db:
                user_stmt = select(User).where(User.id == user_id)
                user = (await db.execute(user_stmt)).scalars().first()
                recipient_email = user.email if user and user.email else settings.ADMIN_EMAIL
            
            email_msg = EmailMessage()
            email_msg["From"] = settings.EMAILS_FROM_EMAIL
            email_msg["To"] = recipient_email
            email_msg["Subject"] = f"[CITMS ALERT] {title}"
            email_msg.set_content(message)

            await aiosmtplib.send(
                email_msg,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USER,
                password=settings.SMTP_PASSWORD,
                use_tls=settings.SMTP_TLS,
            )
            logger.info(f"[EMAIL] Sent alert to {settings.ADMIN_EMAIL}")
        except Exception as e:
            logger.error(f"[EMAIL-ERROR] Failed to send email: {e}")

@shared_task(name="notifications.send_notification_task")
def send_notification_task(user_id: str, title: str, message: str, type_cat: str = "INFO"):
    """ Module 7: Production-ready Notification Dispatch """
    return run_async(_dispatch_notification(user_id, title, message, type_cat))
