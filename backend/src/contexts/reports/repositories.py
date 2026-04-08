from typing import List, Any, Dict
from sqlalchemy import select, text, and_
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.contexts.asset.models import Device
from backend.src.contexts.inventory.models import SoftwareCatalog, SoftwareInstallation
from backend.src.contexts.itsm.models import Ticket, TicketStatus
from backend.src.contexts.license.models import SoftwareLicense
from backend.src.contexts.auth.models import AuditLog, User
from backend.src.contexts.procurement.models import PurchaseOrder, POStatus
from backend.src.contexts.workflow.models import WorkflowRequest, WorkflowType, WorkflowStatus
import uuid

class ReportRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_asset_inventory(self, filters: Dict[str, Any], data_scope: Any) -> List[Any]:
        """Query basic asset inventory with filters."""
        query = select(Device).where(Device.deleted_at == None)
        query = data_scope.apply_isolation(query, Device)
        if filters.get("category"):
            query = query.where(Device.device_type == filters["category"])
        if filters.get("status"):
            query = query.where(Device.status == filters["status"])
            
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_asset_depreciation_from_mv(self) -> List[Any]:
        """Query from mv_asset_depreciation created in Step 2."""
        query = text("SELECT * FROM mv_asset_depreciation ORDER BY current_value DESC")
        result = await self.db.execute(query)
        return result.mappings().all()

    async def get_software_usage_top10_from_mv(self) -> List[Any]:
        """Query from mv_software_usage_top10 created in Step 2."""
        query = text("SELECT * FROM mv_software_usage_top10")
        result = await self.db.execute(query)
        return result.mappings().all()

    async def get_ticket_sla_stats_from_mv(self, data_scope: Any) -> List[Any]:
        """Query from mv_ticket_sla_stats created in Step 2."""
        base_query = "SELECT * FROM mv_ticket_sla_stats"
        
        if not data_scope.is_admin:
            conditions = []
            if data_scope.is_it_staff and data_scope.user.location_id:
                conditions.append(f"location_id = '{data_scope.user.location_id}'")
            if data_scope.is_dept_head and data_scope.user.department_id:
                conditions.append(f"department_id = '{data_scope.user.department_id}'")
            
            if conditions:
                base_query += " WHERE " + " OR ".join(conditions)
                
        result = await self.db.execute(text(base_query))
        return result.mappings().all()

    async def get_offline_missing_devices_from_mv(self) -> List[Any]:
        """Query from mv_offline_missing_devices created in Step 2."""
        query = text("SELECT * FROM mv_offline_missing_devices")
        result = await self.db.execute(query)
        return result.mappings().all()

    async def get_license_expiration_report(self) -> List[Any]:
        """Query licenses expiring in the next 30 days."""
        query = text("""
            SELECT sl.*, sc.name as software_name 
            FROM software_licenses sl
            JOIN software_catalog sc ON sl.software_catalog_id = sc.id
            WHERE sl.expire_date <= CURRENT_DATE + INTERVAL '30 days'
            AND sl.deleted_at IS NULL
        """)
        result = await self.db.execute(query)
        return result.mappings().all()

    async def get_audit_log_report(self, filters: Dict[str, Any]) -> List[Any]:
        """Query audit logs with filters."""
        query = select(AuditLog, User.full_name).join(User, AuditLog.user_id == User.id, isouter=True)
        if filters.get("user_id"):
            query = query.where(AuditLog.user_id == filters["user_id"])
        if filters.get("action"):
            query = query.where(AuditLog.action == filters["action"])
        if filters.get("start_date"):
            query = query.where(AuditLog.created_at >= filters["start_date"])
        if filters.get("end_date"):
            query = query.where(AuditLog.created_at <= filters["end_date"])
            
        query = query.order_by(AuditLog.created_at.desc())
        result = await self.db.execute(query)
        return result.all()

    async def get_procurement_report(self, filters: Dict[str, Any]) -> List[Any]:
        """Query purchase orders with filters."""
        query = select(PurchaseOrder)
        if filters.get("status"):
            query = query.where(PurchaseOrder.status == filters["status"])
        if filters.get("start_date"):
            query = query.where(PurchaseOrder.created_at >= filters["start_date"])
            
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_workflow_report(self, filters: Dict[str, Any]) -> List[Any]:
        """Query workflow requests with filters."""
        query = select(WorkflowRequest)
        if filters.get("type"):
            query = query.where(WorkflowRequest.type == filters["type"])
        if filters.get("status"):
            query = query.where(WorkflowRequest.status == filters["status"])
            
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_remote_session_report(self, filters: Dict[str, Any]) -> List[Any]:
        """Query remote control sessions from audit logs."""
        query = select(AuditLog, User.full_name).join(User, AuditLog.user_id == User.id)
        query = query.where(AuditLog.action == "CREATE_RUSTDESK_SESSION")
        
        if filters.get("start_date"):
            query = query.where(AuditLog.created_at >= filters["start_date"])
            
        result = await self.db.execute(query)
        return result.all()

    async def refresh_all_materialized_views(self):
        """Refresh MVs to ensure data is up to date."""
        views = [
            "mv_asset_depreciation", 
            "mv_software_usage_top10", 
            "mv_ticket_sla_stats", 
            "mv_offline_missing_devices"
        ]
        for view in views:
            await self.db.execute(text(f"REFRESH MATERIALIZED VIEW CONCURRENTLY {view}"))
        await self.db.commit()
