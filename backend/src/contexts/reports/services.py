import pandas as pd
import io
from datetime import datetime
from typing import List, Any, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.contexts.reports.repositories import ReportRepository
from backend.src.contexts.reports.schemas import ReportFilter
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from xhtml2pdf import pisa

class ReportService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ReportRepository(db)

    async def generate_asset_inventory_report(self, filters: ReportFilter, data_scope: Any):
        """Generate asset inventory report and export to requested format."""
        data = await self.repo.get_asset_inventory(filters.dict(), data_scope)
        df = pd.DataFrame([
            {
                "Hostname": d.hostname,
                "Serial": d.serial_number,
                "Type": d.device_type,
                "Status": d.status,
                "Last Seen": d.last_seen.isoformat() if d.last_seen else "Never"
            } for d in data
        ])
        return self._export_dataframe(df, filters.format, "Asset_Inventory")

    async def generate_depreciation_report(self, filters: ReportFilter):
        """Generate asset depreciation report from Materialized View."""
        data = await self.repo.get_asset_depreciation_from_mv()
        df = pd.DataFrame([dict(r) for r in data])
        return self._export_dataframe(df, filters.format, "Asset_Depreciation")

    async def generate_software_usage_report(self, filters: ReportFilter):
        """Generate software usage report from Materialized View."""
        data = await self.repo.get_software_usage_top10_from_mv()
        df = pd.DataFrame([dict(r) for r in data])
        return self._export_dataframe(df, filters.format, "Software_Usage_Top10")

    async def generate_sla_performance_report(self, filters: ReportFilter, data_scope: Any):
        """Generate SLA performance report from Materialized View."""
        data = await self.repo.get_ticket_sla_stats_from_mv(data_scope)
        df = pd.DataFrame([dict(r) for r in data])
        return self._export_dataframe(df, filters.format, "Ticket_SLA_Stats")

    async def generate_offline_missing_report(self, filters: ReportFilter):
        """Generate offline/missing devices report from Materialized View."""
        data = await self.repo.get_offline_missing_devices_from_mv()
        df = pd.DataFrame([dict(r) for r in data])
        return self._export_dataframe(df, filters.format, "Offline_Missing_Devices")

    async def generate_license_expiration_report(self, filters: ReportFilter):
        """Generate license expiration report."""
        data = await self.repo.get_license_expiration_report()
        df = pd.DataFrame([dict(r) for r in data])
        return self._export_dataframe(df, filters.format, "License_Expiration")

    async def generate_audit_log_report(self, filters: ReportFilter):
        """Generate audit log report."""
        data = await self.repo.get_audit_log_report(filters.dict())
        df = pd.DataFrame([
            {
                "Timestamp": r.AuditLog.created_at.isoformat(),
                "User": r.full_name or "System",
                "Action": r.AuditLog.action,
                "Resource": r.AuditLog.resource_type,
                "Status": r.AuditLog.status
            } for r in data
        ])
        return self._export_dataframe(df, filters.format, "Audit_Log")

    async def generate_procurement_report(self, filters: ReportFilter):
        """Generate procurement report."""
        data = await self.repo.get_procurement_report(filters.dict())
        df = pd.DataFrame([
            {
                "PO Number": d.po_number,
                "Status": d.status,
                "Total Amount": d.total_amount,
                "Requested At": d.created_at.isoformat()
            } for d in data
        ])
        return self._export_dataframe(df, filters.format, "Procurement")

    async def generate_workflow_report(self, filters: ReportFilter):
        """Generate workflow report."""
        data = await self.repo.get_workflow_report(filters.dict())
        df = pd.DataFrame([
            {
                "Type": d.type,
                "Status": d.status,
                "Effective Date": d.effective_date.isoformat(),
                "Requested At": d.created_at.isoformat()
            } for d in data
        ])
        return self._export_dataframe(df, filters.format, "Workflow")

    async def generate_remote_session_report(self, filters: ReportFilter):
        """Generate remote session report."""
        data = await self.repo.get_remote_session_report(filters.dict())
        df = pd.DataFrame([
            {
                "Timestamp": r.AuditLog.created_at.isoformat(),
                "User": r.full_name,
                "Device ID": r.AuditLog.resource_id,
                "Status": r.AuditLog.status
            } for r in data
        ])
        return self._export_dataframe(df, filters.format, "Remote_Session")

    def _export_dataframe(self, df: pd.DataFrame, format: str, filename: str):
        """Export pandas DataFrame to requested format."""
        if format == "json":
            return df.to_dict(orient="records")
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        full_filename = f"{filename}_{timestamp}.{format}"
        
        if format == "csv":
            stream = io.StringIO()
            df.to_csv(stream, index=False)
            return StreamingResponse(
                io.BytesIO(stream.getvalue().encode()),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename={full_filename}"}
            )
            
        elif format == "xlsx":
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Report')
            output.seek(0)
            return StreamingResponse(
                output,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": f"attachment; filename={full_filename}"}
            )
            
        elif format == "pdf":
            return self._render_pdf(df, filename, full_filename)
            
        raise HTTPException(status_code=400, detail="Unsupported export format")

    def _render_pdf(self, df: pd.DataFrame, title: str, filename: str):
        """Render DataFrame to PDF using xhtml2pdf."""
        html_content = f"""
        <html>
        <head>
            <style>
                @page {{
                    size: a4 landscape;
                    margin: 1cm;
                    @bottom-right {{
                        content: "Trang " counter(page);
                    }}
                    @bottom-left {{
                        content: "CITMS v3.6 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}";
                    }}
                }}
                body {{ font-family: Helvetica, Arial, sans-serif; font-size: 10pt; }}
                h1 {{ text-align: center; color: #2c3e50; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th, td {{ border: 1px solid #bdc3c7; padding: 8px; text-align: left; }}
                th {{ background-color: #ecf0f1; font-weight: bold; }}
                tr:nth-child(even) {{ background-color: #f9f9f9; }}
            </style>
        </head>
        <body>
            <h1>{title.replace('_', ' ')} Report</h1>
            <table>
                <thead>
                    <tr>
                        {''.join(f'<th>{col}</th>' for col in df.columns)}
                    </tr>
                </thead>
                <tbody>
                    {''.join(f"<tr>{''.join(f'<td>{val}</td>' for val in row)}</tr>" for row in df.values)}
                </tbody>
            </table>
        </body>
        </html>
        """
        
        result = io.BytesIO()
        pisa_status = pisa.CreatePDF(io.BytesIO(html_content.encode("utf-8")), dest=result)
        
        if pisa_status.err:
            raise HTTPException(status_code=500, detail="Failed to generate PDF report")
            
        result.seek(0)
        return StreamingResponse(
            result,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
