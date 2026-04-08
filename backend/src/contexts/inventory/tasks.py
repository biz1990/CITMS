from celery import shared_task
from backend.src.infrastructure.database import AsyncSessionLocal
from backend.src.contexts.inventory.models import InventoryRunLog
from sqlalchemy import delete, text
from datetime import datetime, timedelta
import asyncio

@shared_task(name="inventory.cleanup_logs")
def cleanup_inventory_logs_task(days: int = 30):
    """Cleanup old inventory run logs."""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_async_cleanup_logs(days))

async def _async_cleanup_logs(days: int):
    threshold = datetime.utcnow() - timedelta(days=days)
    async with AsyncSessionLocal() as db:
        try:
            # Delete logs older than threshold
            stmt = delete(InventoryRunLog).where(InventoryRunLog.created_at < threshold)
            result = await db.execute(stmt)
            await db.commit()
            print(f"Cleaned up {result.rowcount} inventory run logs older than {days} days.")
        except Exception as e:
            print(f"Error cleaning up inventory logs: {str(e)}")
            await db.rollback()
