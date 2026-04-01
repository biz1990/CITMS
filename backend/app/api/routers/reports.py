from typing import Any
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
import io

from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db
from app.api.auth_deps import RequireRole

router = APIRouter()

@router.get("/export/devices")
async def export_devices(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(RequireRole("settings:read"))
) -> Any:
    # Placeholder for Excel generation using pandas/openpyxl
    output = io.StringIO()
    output.write("id,hostname,mac,status\n")
    output.write("1,deviceA,00:11:22,IN_USE\n")
    
    response = StreamingResponse(iter([output.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=export.csv"
    return response
