from celery import shared_task
from backend.src.infrastructure.database import SessionLocal
from backend.src.contexts.reports.repositories import ReportRepository
from backend.src.contexts.reports.services import ReportService
from backend.src.contexts.reports.schemas import ReportFilter
import asyncio
from datetime import datetime

@shared_task(name="reports.refresh_mvs")
def refresh_materialized_views_task():
    """Refresh all materialized views daily at 01:00 AM."""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_async_refresh_mvs())

async def _async_refresh_mvs():
    async with SessionLocal() as db:
        repo = ReportRepository(db)
        await repo.refresh_all_materialized_views()
        print(f"Materialized Views refreshed at {datetime.now()}")

@shared_task(name="reports.monthly_auto_report")
def monthly_auto_report_task():
    """Generate and send monthly auto reports on the 1st of every month."""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_async_monthly_report())

async def _async_monthly_report():
    async with SessionLocal() as db:
        service = ReportService(db)
        filters = ReportFilter(format="xlsx")
        
        # Generate reports
        asset_report = await service.generate_asset_inventory_report(filters)
        sla_report = await service.generate_sla_performance_report(filters)
        
        # Simulation: Send reports via Email to IT Manager
        # In real app, call NotificationService.send_email_with_attachments
        print(f"Monthly reports generated and sent at {datetime.now()}")
