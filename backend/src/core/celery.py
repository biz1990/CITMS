from celery import Celery
from celery.schedules import crontab
from backend.src.core.config import settings

celery_app = Celery(
    "citms_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.task_routes = {
    "backend.src.tasks.*": {"queue": "citms_queue"}
}

celery_app.autodiscover_tasks([
    "backend.src.contexts.notification",
    "backend.src.contexts.inventory",
    "backend.src.contexts.license"
])

celery_app.conf.beat_schedule = {
    "check-license-compliance-daily": {
        "task": "license.check_compliance",
        "schedule": crontab(hour=3, minute=0), # 3 AM daily
    },
    "cleanup-inventory-logs-daily": {
        "task": "inventory.cleanup_logs",
        "schedule": crontab(hour=2, minute=0), # 2 AM daily
        "args": (30,) # 30 days
    },
    "cleanup-redis-streams-hourly": {
        "task": "notification.cleanup_streams",
        "schedule": crontab(minute=0), # Every hour
        "args": (1000,) # Max 1000 messages
    }
}
