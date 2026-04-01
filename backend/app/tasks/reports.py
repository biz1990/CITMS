from celery import shared_task
from app.core.async_runner import run_async
from app.api.deps import AsyncSessionLocal
import datetime

async def _generate_report():
    async with AsyncSessionLocal() as db:
        # Complex aggregation across tickets/inventory via DB
        # Save to S3/MinIO and link
        print(f"[CELERY-REPORT] Generating ITSM & Asset monthly summary for {datetime.date.today().strftime('%B %Y')}")
        # Could spawn secondary notification task here

@shared_task(name="reports.generate_monthly_report_task")
def generate_monthly_report_task():
    return run_async(_generate_report())
