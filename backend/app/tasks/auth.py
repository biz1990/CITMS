from celery import shared_task
from app.core.async_runner import run_async
from app.api.deps import AsyncSessionLocal
from app.services.auth import AuthService

async def _sync_ldap():
    async with AsyncSessionLocal() as db:
        svc = AuthService(db)
        result = await svc.ldap_sync()
        print(f"[CELERY-LDAP] Synchronized AD Directory. {result.get('synced_users', 0)} users updated.")

@shared_task(name="auth.ldap_ad_sync_task")
def ldap_ad_sync_task():
    return run_async(_sync_ldap())
