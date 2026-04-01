import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.ticket import Ticket
from app.models.user import User

logger = logging.getLogger(__name__)

class ITSMService:
    TICKET_STATES = {
        "OPEN": ["ASSIGNED", "CANCELLED"],
        "ASSIGNED": ["IN_PROGRESS", "CANCELLED"],
        "IN_PROGRESS": ["PENDING", "RESOLVED", "CANCELLED"],
        "PENDING": ["IN_PROGRESS", "CANCELLED"],
        "RESOLVED": ["IN_PROGRESS", "CLOSED", "CANCELLED"],
        "CLOSED": [],
        "CANCELLED": []
    }

    SLA_HOURS = {
        "CRITICAL": 4,
        "HIGH": 8,
        "MEDIUM": 24,
        "LOW": 72
    }

    def __init__(self, db: AsyncSession):
        self.db = db

    def _add_business_hours(self, start_time: datetime, hours_to_add: int) -> datetime:
        """SLA calculation based on business hours"""
        current_time = start_time
        remaining_hours = hours_to_add
        while remaining_hours > 0:
            current_time += timedelta(hours=1)
            # Skip weekends (5=Sat, 6=Sun)
            if current_time.weekday() < 5:
                # 08:00 - 17:00
                if 8 <= current_time.hour < 17:
                    remaining_hours -= 1
        return current_time

    async def advance_state(self, ticket_id: uuid.UUID, new_state: str) -> bool:
        """Module 4: State Machine logic for tickets"""
        stmt = select(Ticket).where(Ticket.id == ticket_id)
        ticket = (await self.db.execute(stmt)).scalars().first()
        if not ticket:
            return False
            
        current_state = ticket.status
        if new_state not in self.TICKET_STATES.get(current_state, []):
            raise ValueError(f"State Machine Violation: Cannot transition {current_state} -> {new_state}")
            
        ticket.status = new_state
        ticket.version += 1 # Optimistic locking enforced
        await self.db.commit()
        return True

    async def check_escalation_rules(self):
        """
        Module 7.2: Ticket Escalation Rules 
        - Rule 1: SLA Breach -> Add SLA_BREACHED tag/notes
        - Rule 2: Inactivity PENDING > 7 days -> Auto-RESOLVED
        """
        now = datetime.utcnow()
        
        # Rule 1: SLA Breach
        stmt1 = select(Ticket).where(
            Ticket.status.in_(["OPEN", "ASSIGNED", "IN_PROGRESS"]),
            Ticket.sla_resolution_due < now
        )
        breached_tickets = (await self.db.execute(stmt1)).scalars().all()
        for t in breached_tickets:
            if "[AUTO] SLA BREACHED ESCALATION!" not in str(t.resolution_notes):
                t.resolution_notes = (t.resolution_notes or "") + "\n[AUTO] SLA BREACHED ESCALATION!"
                t.version += 1
                logger.warning(f"Escalation Action: SLA Breached on ticket {t.ticket_code}.")

        # Rule 2: Inactivity PENDING > 7 days
        stmt2 = select(Ticket).where(
            Ticket.status == "PENDING",
            Ticket.updated_at < now - timedelta(days=7)
        )
        inactive_tickets = (await self.db.execute(stmt2)).scalars().all()
        for t in inactive_tickets:
            t.status = "RESOLVED"
            t.resolution_notes = (t.resolution_notes or "") + "\n[AUTO] Resolved due to 7 days inactivity."
            t.version += 1
            logger.info(f"Escalation Action: Inactivity Resolution on {t.ticket_code}.")
            
        await self.db.commit()

    async def priority_bump_check(self, user_id: uuid.UUID):
        """
        Rule 3: User Priority Bump 
        1 User created > 3 HIGH tickets in 24h -> Bump new/existing to CRITICAL.
        """
        now = datetime.utcnow()
        stmt = select(Ticket).where(
            Ticket.created_by == user_id, 
            Ticket.priority == "HIGH",
            Ticket.created_at >= now - timedelta(hours=24)
        )
        recent_highs = (await self.db.execute(stmt)).scalars().all()
        if len(recent_highs) > 3:
            for t in recent_highs:
                t.priority = "CRITICAL"
                t.version += 1
            logger.critical(f"Priority bump triggered! Auto-promoting {len(recent_highs)} tickets for User {user_id}.")
            await self.db.commit()

    async def auto_create_ticket_for_violation(self, payload: Dict[str, Any]):
        """Subscriber for License violation event to auto-create Escalated Ticket"""
        title_tag = f"[CRITICAL EVENT] Vi phạm Bản quyền {payload.get('software')}"
        stmt = select(Ticket).where(Ticket.title == title_tag, Ticket.status.in_(["OPEN", "ASSIGNED", "IN_PROGRESS"]))
        existing = (await self.db.execute(stmt)).scalars().first()
        if existing:
            return False
            
        ticket = Ticket(
            ticket_code=f"ITSM-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            title=title_tag,
            description=f"Hệ thống tự động phát hiện vi phạm bản quyền: Vượt quá {payload.get('excess')} seats cấp phép.",
            priority="CRITICAL",
            category="SOFTWARE_COMPLIANCE"
        )
        ticket.sla_resolution_due = self._add_business_hours(datetime.utcnow(), self.SLA_HOURS["CRITICAL"])
        self.db.add(ticket)
        await self.db.commit()
        return True
