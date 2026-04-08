from datetime import datetime, time, timedelta
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.contexts.itsm.models import SystemHoliday, TicketPriority

class SlaService:
    def __init__(self, db: AsyncSession):
        self.db = db
        # Business hours: 08:00 - 17:00
        self.work_start = time(8, 0)
        self.work_end = time(17, 0)
        # Lunch break: 12:00 - 13:00 (1 hour)
        self.lunch_start = time(12, 0)
        self.lunch_end = time(13, 0)

    async def calculate_deadline(self, start_time: datetime, priority: TicketPriority) -> datetime:
        """Calculate SLA deadline based on business hours and holidays."""
        # SLA hours by priority
        sla_hours = {
            TicketPriority.LOW: 48,
            TicketPriority.MEDIUM: 24,
            TicketPriority.HIGH: 8,
            TicketPriority.CRITICAL: 4
        }.get(priority, 24)

        # Get holidays from DB
        res = await self.db.execute(select(SystemHoliday.holiday_date))
        holidays = {h.date() for h in res.scalars().all()}

        current_time = start_time
        remaining_hours = sla_hours

        while remaining_hours > 0:
            # Move to next business day if current time is outside business hours
            if not self._is_business_day(current_time, holidays) or current_time.time() >= self.work_end:
                current_time = self._move_to_next_business_day(current_time, holidays)
                continue
            
            if current_time.time() < self.work_start:
                current_time = current_time.replace(hour=self.work_start.hour, minute=0, second=0)

            # Calculate available time in current day
            day_end = current_time.replace(hour=self.work_end.hour, minute=0, second=0)
            
            # Handle lunch break
            lunch_s = current_time.replace(hour=self.lunch_start.hour, minute=0, second=0)
            lunch_e = current_time.replace(hour=self.lunch_end.hour, minute=0, second=0)

            if current_time < lunch_s:
                available_before_lunch = (lunch_s - current_time).total_seconds() / 3600
                if remaining_hours <= available_before_lunch:
                    current_time += timedelta(hours=remaining_hours)
                    remaining_hours = 0
                else:
                    remaining_hours -= available_before_lunch
                    current_time = lunch_e # Skip lunch
            elif current_time < lunch_e:
                current_time = lunch_e # Skip lunch
                continue
            else:
                available_after_lunch = (day_end - current_time).total_seconds() / 3600
                if remaining_hours <= available_after_lunch:
                    current_time += timedelta(hours=remaining_hours)
                    remaining_hours = 0
                else:
                    remaining_hours -= available_after_lunch
                    current_time = self._move_to_next_business_day(current_time, holidays)

        return current_time

    def _is_business_day(self, dt: datetime, holidays: set) -> bool:
        return dt.weekday() < 5 and dt.date() not in holidays

    def _move_to_next_business_day(self, dt: datetime, holidays: set) -> datetime:
        next_day = dt + timedelta(days=1)
        next_day = next_day.replace(hour=self.work_start.hour, minute=0, second=0)
        while not self._is_business_day(next_day, holidays):
            next_day += timedelta(days=1)
        return next_day
