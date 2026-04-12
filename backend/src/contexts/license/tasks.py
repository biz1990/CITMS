import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.contexts.license.models import SoftwareLicense
from backend.src.infrastructure.database import SessionLocal
from backend.src.contexts.notification.services.notifier import NotificationService
from backend.src.infrastructure.repositories.base import BaseRepository
from backend.src.contexts.notification.models import Notification
import logging

logger = logging.getLogger(__name__)

from backend.src.core.celery import celery_app
import asyncio

@celery_app.task(name="license.check_compliance")
def check_license_compliance_task():
    """
    Celery task wrapper for license compliance check.
    """
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(check_license_compliance())

async def check_license_compliance():
    """
    Background task to check for license compliance violations (SRS §3.3).
    Identifies licenses where used_seats > total_seats.
    """
    logger.info("Starting license compliance check...")
    async with SessionLocal() as db:
        try:
            # 1. Find violations
            query = select(SoftwareLicense).where(SoftwareLicense.used_seats > SoftwareLicense.total_seats)
            result = await db.execute(query)
            violations = result.scalars().all()
            
            if not violations:
                logger.info("No license compliance violations found.")
                return

            # 2. Notify IT Managers
            # For simplicity, we'll notify all users with IT_MANAGER role
            # In a real app, this would be more targeted
            for license in violations:
                msg = f"License Violation: {license.id} has {license.used_seats} used seats but only {license.total_seats} total seats."
                logger.warning(msg)
                
                # Emit notification (this would call the notification service)
                # For now, we'll just log it. In a full implementation, we'd create Notification records.
                # await notification_service.create_system_notification(
                #     title="License Compliance Violation",
                #     message=msg,
                #     priority="CRITICAL"
                # )
                
        except Exception as e:
            logger.error(f"Error during license compliance check: {str(e)}")
            await db.rollback()
