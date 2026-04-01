from celery import shared_task
from app.core.async_runner import run_async
from app.api.deps import AsyncSessionLocal
from app.services.itsm import ITSMService

async def _itsm_sla_check():
    async with AsyncSessionLocal() as db:
        svc = ITSMService(db)
        await svc.check_escalation_rules()
        print("[CELERY-ITSM] Completed SLA and Escalation sweep.")

@shared_task(name="itsm.check_escalation_rules_task")
def check_escalation_rules_task():
    return run_async(_itsm_sla_check())
