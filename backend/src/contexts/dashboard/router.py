from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text, and_, or_
from backend.src.infrastructure.database import get_db
from backend.src.contexts.itsm.models import Ticket, TicketStatus
from backend.src.contexts.asset.models import Device
from backend.src.contexts.license.models import SoftwareLicense
from backend.src.contexts.auth.dependencies import get_current_user
from backend.src.contexts.auth.models import User
from typing import Dict, Any
from datetime import datetime, timedelta

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/stats")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns real-time statistics for the dashboard.
    """
    now = datetime.utcnow()
    five_mins_ago = now - timedelta(minutes=5)
    one_day_ago = now - timedelta(days=1)
    
    # 1. Ticket Counts by Status
    ticket_status_query = select(Ticket.status, func.count(Ticket.id)).group_by(Ticket.status)
    ticket_status_res = await db.execute(ticket_status_query)
    status_counts = {status: count for status, count in ticket_status_res.all()}
    
    # 2. Total Tickets
    total_tickets_query = select(func.count(Ticket.id))
    total_tickets = (await db.execute(total_tickets_query)).scalar() or 0
    
    # 3. SLA Breach Count
    sla_breach_query = select(func.count(Ticket.id)).where(Ticket.is_sla_breached == True)
    sla_breaches = (await db.execute(sla_breach_query)).scalar() or 0
    
    # 4. Asset Stats
    asset_count_query = select(func.count(Device.id))
    total_assets = (await db.execute(asset_count_query)).scalar() or 0
    
    asset_status_query = select(Device.status, func.count(Device.id)).group_by(Device.status)
    asset_status_res = await db.execute(asset_status_query)
    asset_status_counts = {status: count for status, count in asset_status_res.all()}
    
    # 5. Agent Health
    online_count = (await db.execute(select(func.count(Device.id)).where(Device.last_seen >= five_mins_ago))).scalar() or 0
    offline_count = (await db.execute(select(func.count(Device.id)).where(and_(Device.last_seen < five_mins_ago, Device.last_seen >= one_day_ago)))).scalar() or 0
    missing_count = (await db.execute(select(func.count(Device.id)).where(or_(Device.last_seen < one_day_ago, Device.last_seen == None)))).scalar() or 0
    
    # 5b. Identification Alerts
    invalid_serial_count = (await db.execute(select(func.count(Device.id)).where(Device.invalid_serial == True))).scalar() or 0
    # Count devices with more than 1 MAC in alternative_macs
    mac_change_count = (await db.execute(
        select(func.count(Device.id)).where(func.jsonb_array_length(Device.alternative_macs) > 1)
    )).scalar() or 0

    # 6. Weekly Ticket Count (Last 7 days)
    weekly_tickets = []
    for i in range(6, -1, -1):
        day = now - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day.replace(hour=23, minute=59, second=59, microsecond=999999)
        count = (await db.execute(select(func.count(Ticket.id)).where(and_(Ticket.created_at >= day_start, Ticket.created_at <= day_end)))).scalar() or 0
        weekly_tickets.append({"day": day.strftime("%a"), "count": count})

    # 7. Timeline (Expirations in next 90 days)
    ninety_days_later = now + timedelta(days=90)
    
    expiring_licenses = (await db.execute(
        select(SoftwareLicense.id, SoftwareLicense.type, SoftwareLicense.expire_date)
        .where(and_(SoftwareLicense.expire_date >= now, SoftwareLicense.expire_date <= ninety_days_later))
        .limit(5)
    )).all()
    
    # 8. Recent Activity (Last 10 tickets)
    recent_tickets_query = select(Ticket).order_by(Ticket.created_at.desc()).limit(10)
    recent_tickets = (await db.execute(recent_tickets_query)).scalars().all()
    
    return {
        "tickets": {
            "total": total_tickets,
            "by_status": status_counts,
            "sla_breaches": sla_breaches,
            "weekly_count": weekly_tickets
        },
        "assets": {
            "total": total_assets,
            "by_status": asset_status_counts
        },
        "agent_health": {
            "online": online_count,
            "offline": offline_count,
            "missing": missing_count,
            "health_score": round((online_count / total_assets * 100), 1) if total_assets > 0 else 100,
            "invalid_serials": invalid_serial_count,
            "mac_changes": mac_change_count
        },
        "timeline": [
            {
                "id": str(l.id),
                "type": "LICENSE",
                "title": f"License Expiry: {l.type}",
                "date": l.expire_date.isoformat()
            } for l in expiring_licenses
        ],
        "recent_activity": [
            {
                "id": str(t.id),
                "title": t.title,
                "status": t.status,
                "created_at": t.created_at.isoformat() if t.created_at else None
            } for t in recent_tickets
        ]
    }
