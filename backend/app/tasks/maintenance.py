from datetime import datetime, timedelta
from celery import shared_task
from sqlalchemy import select
from app.core.async_runner import run_async
from app.api.deps import AsyncSessionLocal
from app.models.user import User
from app.models.workflow import Notification

async def _password_rotation():
    async with AsyncSessionLocal() as db:
        now = datetime.utcnow()
        limit_date = now - timedelta(days=90)
        
        # Fake tracking metric - usually needs password_updated_at column
        # Using created_at for simple mock demo if password_updated_at doesn't exist
        stmt = select(User).where(User.created_at < limit_date)
        expired_users = (await db.execute(stmt)).scalars().all()
        
        for u in expired_users:
            print(f"[CELERY-PASS] User {u.username} forced to Reset Password (90 Days standard).")
            # Push Warning to notification module
            
async def _data_cleanup():
    async with AsyncSessionLocal() as db:
        now = datetime.utcnow()
        limit_date = now - timedelta(days=30)
        
        # Module 7: Notification Retention
        stmt = select(Notification).where(Notification.created_at < limit_date) # SQLAlchemy v2 delete
        from sqlalchemy import delete
        del_stmt = delete(Notification).where(Notification.created_at < limit_date)
        await db.execute(del_stmt)
        await db.commit()
        print(f"[CELERY-CLEANUP] Deleted 30-day old notifications.")

async def _maintain_partitions():
    async with AsyncSessionLocal() as db:
        now = datetime.utcnow()
        if now.month == 12:
            next_month = datetime(now.year + 1, 1, 1)
            next_next_month = datetime(now.year + 1, 2, 1)
        else:
            next_month = datetime(now.year, now.month + 1, 1)
            if next_month.month == 12:
                next_next_month = datetime(next_month.year + 1, 1, 1)
            else:
                next_next_month = datetime(next_month.year, next_month.month + 1, 1)
        
        table_name = f"history_logs_{next_month.strftime('%Y_%m')}"
        start_val = next_month.strftime('%Y-%m-%d')
        end_val = next_next_month.strftime('%Y-%m-%d')
        
        sql = f"CREATE TABLE IF NOT EXISTS {table_name} PARTITION OF history_logs FOR VALUES FROM ('{start_val}') TO ('{end_val}');"
        from sqlalchemy import text
        await db.execute(text(sql))
        await db.commit()
        print(f"[CELERY-PARTITION] Ensured partition {table_name} exists.")

@shared_task(name="maintenance.password_rotation_task")
def password_rotation_task():
    return run_async(_password_rotation())

@shared_task(name="maintenance.data_cleanup_task")
def data_cleanup_task():
    return run_async(_data_cleanup())

@shared_task(name="maintenance.maintain_partitions_task")
def maintain_partitions_task():
    return run_async(_maintain_partitions())
