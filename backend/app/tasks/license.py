from celery import shared_task
from sqlalchemy import select
from app.core.async_runner import run_async
from app.api.deps import AsyncSessionLocal
from app.models.software import SoftwareLicense
from app.services.license import LicenseService

async def _audit_licenses():
    async with AsyncSessionLocal() as db:
        svc = LicenseService(db)
        stmt = select(SoftwareLicense.id)
        license_ids = (await db.execute(stmt)).scalars().all()
        for lid in license_ids:
            # check_compliance naturally emits events if bad
            await svc.check_compliance(lid)
        print(f"[CELERY-LICENSE] Compliancy checked for {len(license_ids)} active licenses.")

@shared_task(name="license.audit_violations_task")
def audit_violations_task():
    return run_async(_audit_licenses())
