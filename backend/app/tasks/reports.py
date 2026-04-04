import uuid
import logging
import datetime
import io
import aioboto3
from celery import shared_task

from app.core.async_runner import run_async
from app.api.deps import AsyncSessionLocal
from app.services.reports_service import ReportsService
from app.core.config import settings
from app.tasks.notifications import send_notification_task

logger = logging.getLogger(__name__)

async def _save_to_s3(file_name: str, data: bytes):
    """Module 8: Actual S3/MinIO persistence"""
    session = aioboto3.Session()
    async with session.client(
        "s3",
        endpoint_url=f"http://{settings.S3_ENDPOINT}" if not settings.S3_SECURE else f"https://{settings.S3_ENDPOINT}",
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY,
        use_ssl=settings.S3_SECURE
    ) as s3:
        await s3.put_object(
            Bucket=settings.S3_BUCKET_REPORTS,
            Key=file_name,
            Body=data
        )
    logger.info(f"[REPORT-S3] Successfully archived {file_name} to bucket {settings.S3_BUCKET_REPORTS}")

async def _generate_all_monthly_reports():
    async with AsyncSessionLocal() as db:
        svc = ReportsService(db)
        report_types = [
            "ram_inventory", "software_usage", "component_summary",
            "asset_overview", "depreciation", "inventory_status",
            "offline_devices", "repair_costs", "procurement_costs", "ticket_sla"
        ]
        
        timestamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        for r_type in report_types:
            try:
                excel_data = await svc.export_excel(r_type, None)
                file_name = f"monthly_{r_type}_{timestamp}.xlsx"
                
                # Module 8: Production Archival
                await _save_to_s3(file_name, excel_data)
                
            except Exception as e:
                logger.error(f"[REPORT-TASK-ERROR] Failed to archive {r_type}: {e}")

        # Notify admin of completion
        if settings.ADMIN_EMAIL:
            send_notification_task.delay(
                str(uuid.UUID(int=0)), # System User
                "Monthly Reports Archived",
                f"9/9 reports for {datetime.date.today().strftime('%B %Y')} have been archived to cloud storage.",
                "INFO"
            )

@shared_task(name="reports.generate_monthly_report_task")
def generate_monthly_report_task():
    """ Module 8: Monthly automated reporting cycle (Production) """
    return run_async(_generate_all_monthly_reports())
