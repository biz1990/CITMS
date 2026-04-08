from datetime import datetime, timedelta
from celery import shared_task
from sqlalchemy import select, and_, update
from backend.src.infrastructure.database import SessionLocal
from backend.src.contexts.itsm.models import Ticket, TicketStatus, TicketPriority
from backend.src.contexts.inventory.services.events import InventoryEventPublisher
import asyncio

@shared_task(name="itsm.check_sla_breach")
def check_sla_breach():
    """Check for SLA breaches and update flags."""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_async_check_sla())

async def _async_check_sla():
    async with SessionLocal() as db:
        now = datetime.utcnow()
        
        # 1. Detect Breached Tickets
        res = await db.execute(
            select(Ticket).where(
                and_(
                    Ticket.status.in_([TicketStatus.OPEN, TicketStatus.ASSIGNED, TicketStatus.IN_PROGRESS]),
                    Ticket.sla_deadline < now,
                    Ticket.is_sla_breached == False
                )
            )
        )
        breached_tickets = res.scalars().all()
        
        for ticket in breached_tickets:
            ticket.is_sla_breached = True
            # Publish event for Notification Engine
            await InventoryEventPublisher.publish("TICKET_SLA_BREACHED", ticket.id, {
                "title": ticket.title,
                "priority": ticket.priority,
                "deadline": ticket.sla_deadline.isoformat()
            })

        # 2. Escalation (80% SLA)
        res = await db.execute(
            select(Ticket).where(
                and_(
                    Ticket.status.in_([TicketStatus.OPEN, TicketStatus.ASSIGNED, TicketStatus.IN_PROGRESS]),
                    Ticket.sla_deadline > now,
                    Ticket.sla_deadline < now + timedelta(hours=1), # Approaching 80%
                    Ticket.priority != TicketPriority.CRITICAL
                )
            )
        )
        near_breach_tickets = res.scalars().all()
        for ticket in near_breach_tickets:
            # Auto-bump priority
            ticket.priority = TicketPriority.CRITICAL
            await InventoryEventPublisher.publish("TICKET_NEAR_BREACH", ticket.id, {
                "title": ticket.title,
                "priority": "CRITICAL (Auto-Escalated)"
            })

        # 3. Auto-reassignment for unassigned tickets near breach
        res = await db.execute(
            select(Ticket).where(
                and_(
                    Ticket.status == TicketStatus.OPEN,
                    Ticket.assignee_id == None,
                    Ticket.sla_deadline < now + timedelta(minutes=30)
                )
            )
        )
        unassigned_near_breach = res.scalars().all()
        for ticket in unassigned_near_breach:
            # Simple auto-assignment to first available admin (mock logic)
            # In production, this would use a round-robin or workload-based algorithm
            from backend.src.contexts.auth.models import User
            admin_res = await db.execute(select(User).limit(1)) # Simplified
            admin = admin_res.scalar_one_or_none()
            if admin:
                ticket.assignee_id = admin.id
                ticket.status = TicketStatus.ASSIGNED
                await InventoryEventPublisher.publish("TICKET_AUTO_ASSIGNED", ticket.id, {
                    "title": ticket.title,
                    "assignee": admin.full_name
                })

        await db.commit()
