from fastapi import APIRouter
from app.api.routers import (
    auth, devices, inventory, itsm, 
    procurement, vendors, workflow, license, reports, admin
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Auth & Security"])
api_router.include_router(devices.router, prefix="/devices", tags=["Asset Tracking"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["Inventory Management"])
api_router.include_router(vendors.router, prefix="/vendors", tags=["Vendors & Contracts"])
api_router.include_router(procurement.router, prefix="/procurement", tags=["Procurement & PO Lifecycle"])
api_router.include_router(itsm.router, prefix="/itsm", tags=["ITSM Process"])
api_router.include_router(workflow.router, prefix="/workflows", tags=["On/Offboarding Request System"])
api_router.include_router(license.router, prefix="/licenses", tags=["Software & License Management"])
api_router.include_router(reports.router, prefix="/reports", tags=["Data Export & Logs"])
api_router.include_router(admin.router, prefix="/admin", tags=["Settings & RBAC Mapping"])
