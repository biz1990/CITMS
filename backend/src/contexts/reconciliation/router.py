from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, update, func
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from backend.src.infrastructure.database import get_db
from backend.src.contexts.inventory.models import ReconciliationConflict
from backend.src.contexts.asset.models import Device
from backend.src.contexts.auth.dependencies import get_current_user
from backend.src.contexts.auth.models import User
from backend.src.contexts.auth.audit_service import AuditService

router = APIRouter(prefix="/reconciliation", tags=["Reconciliation"])

@router.get("/conflicts")
async def list_conflicts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    res = await db.execute(
        select(ReconciliationConflict, Device.hostname)
        .join(Device, ReconciliationConflict.device_id == Device.id)
        .where(ReconciliationConflict.status == "PENDING")
    )
    conflicts = []
    for c, hostname in res.all():
        conflicts.append({
            "id": str(c.id),
            "device_id": str(c.device_id),
            "hostname": hostname,
            "field_name": c.field_name,
            "agent_value": c.agent_value,
            "manual_value": c.manual_value,
            "agent_reported_at": c.agent_reported_at.isoformat(),
            "server_updated_at": c.server_updated_at.isoformat()
        })
    return conflicts

@router.post("/conflicts/{id}/resolve")
async def resolve_conflict(
    id: UUID,
    resolution: dict, # {"choice": "AGENT" | "MANUAL"}
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    choice = resolution.get("choice")
    if choice not in ["AGENT", "MANUAL"]:
        raise HTTPException(status_code=400, detail="Invalid choice")
    
    res = await db.execute(select(ReconciliationConflict).where(ReconciliationConflict.id == id))
    conflict = res.scalar_one_or_none()
    if not conflict:
        raise HTTPException(status_code=404, detail="Conflict not found")
    
    # Update device if AGENT data is chosen
    if choice == "AGENT":
        await db.execute(
            update(Device)
            .where(Device.id == conflict.device_id)
            .values({conflict.field_name: conflict.agent_value})
        )
    
    conflict.status = "RESOLVED"
    conflict.resolution_choice = choice
    await db.commit()
    
    return {"status": "resolved"}

@router.post("/auto-merge")
async def auto_merge_devices(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Automatically merges devices that have the same hostname, manufacturer, and model
    but different MAC addresses (e.g. when a USB WiFi dongle is used).
    """
    # This is a complex logic, for now we implement a simplified version
    # that finds devices with invalid serials and same hostname/motherboard
    
    # 1. Find potential duplicates
    res = await db.execute(
        select(Device.hostname, Device.manufacturer, Device.model)
        .where(and_(Device.deleted_at == None, Device.invalid_serial == True))
        .group_by(Device.hostname, Device.manufacturer, Device.model)
        .having(func.count(Device.id) > 1)
    )
    duplicates = res.all()
    
    merged_count = 0
    for hostname, manufacturer, model in duplicates:
        # Get all devices matching this
        res = await db.execute(
            select(Device)
            .where(and_(
                Device.hostname == hostname,
                Device.manufacturer == manufacturer,
                Device.model == model,
                Device.deleted_at == None
            ))
            .order_by(Device.created_at.asc())
        )
        devices = res.scalars().all()
        
        if len(devices) < 2: continue
        
        main_device = devices[0]
        others = devices[1:]
        
        for other in others:
            # Merge alternative macs
            main_macs = main_device.alternative_macs or []
            other_macs = other.alternative_macs or []
            
            # Add other's primary mac to main's alternative macs
            if other.primary_mac:
                main_macs.append({
                    "mac": other.primary_mac,
                    "type": "MERGED",
                    "first_seen": other.created_at.isoformat()
                })
            
            # Add other's alternative macs
            main_macs.extend(other_macs)
            
            # Remove duplicates in main_macs
            seen = set()
            unique_macs = []
            for m in main_macs:
                if m["mac"] not in seen:
                    unique_macs.append(m)
                    seen.add(m["mac"])
            
            main_device.alternative_macs = unique_macs
            other.deleted_at = datetime.utcnow()
            merged_count += 1
            
    await db.commit()
    return {"status": "success", "merged_count": merged_count}
