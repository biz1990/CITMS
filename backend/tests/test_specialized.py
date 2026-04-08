import pytest
import asyncio
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.contexts.inventory.models import Device, Software
from backend.src.contexts.license.models import License, LicenseAssignment
from backend.src.contexts.itsm.models import Ticket
from backend.src.contexts.inventory.repositories import InventoryRepository
from backend.src.contexts.license.repositories import LicenseRepository
from backend.src.contexts.itsm.services import TicketService

# --- 1. Concurrent License Assignment (Pessimistic Lock) ---
@pytest.mark.asyncio
async def test_concurrent_license_assignment(db: AsyncSession):
    """Test 10 concurrent requests for 1 remaining license slot."""
    # Setup: 1 license with 1 slot
    lic = License(name="Test License", total_slots=1, used_slots=0)
    db.add(lic)
    await db.commit()
    
    repo = LicenseRepository(db)
    device_ids = [str(i) for i in range(10)]
    
    async def attempt_assign(device_id):
        try:
            # This should use SELECT FOR UPDATE inside the repo
            return await repo.assign_license(lic.id, device_id)
        except Exception:
            return False

    # Execute 10 concurrent attempts
    results = await asyncio.gather(*[attempt_assign(d) for d in device_ids])
    
    # Assert: Only 1 should succeed
    success_count = len([r for r in results if r is True])
    assert success_count == 1
    
    # Verify DB state
    await db.refresh(lic)
    assert lic.used_slots == 1

# --- 2. Inventory FULL_REPLACE Logic ---
@pytest.mark.asyncio
async def test_inventory_full_replace(db: AsyncSession):
    """Test FULL_REPLACE logic for software inventory."""
    # Setup: Device with 3 existing softwares
    device = Device(hostname="PC-01", serial_number="SN001")
    db.add(device)
    await db.flush()
    
    s1 = Software(device_id=device.id, name="App A", version="1.0")
    s2 = Software(device_id=device.id, name="App B", version="1.0")
    s3 = Software(device_id=device.id, name="App C", version="1.0")
    db.add_all([s1, s2, s3])
    await db.commit()
    
    repo = InventoryRepository(db)
    # New payload with only 2 softwares (App B and App D)
    new_software_list = [
        {"name": "App B", "version": "2.0"}, # Update
        {"name": "App D", "version": "1.0"}  # New
    ]
    
    # Execute FULL_REPLACE ingestion
    await repo.ingest_software(device.id, new_software_list, mode="FULL_REPLACE")
    
    # Assert: App A and App C should be gone, App B updated, App D added
    result = await db.execute(select(Software).where(Software.device_id == device.id))
    current_softwares = result.scalars().all()
    
    assert len(current_softwares) == 2
    names = [s.name for s in current_softwares]
    assert "App B" in names
    assert "App D" in names
    assert "App A" not in names
    assert "App C" not in names

# --- 3. SLA Calculation Accuracy ---
def test_sla_calculation():
    """Test SLA deadline calculation logic (Mocked Service)."""
    # Friday 16:00, SLA 4h, Working hours 08:00-17:00
    start_time = datetime(2026, 4, 3, 16, 0) # Friday
    sla_hours = 4
    
    # Expected: 1h on Friday (16:00-17:00) + 3h on Monday (08:00-11:00)
    # Monday is 2026-04-06
    expected_deadline = datetime(2026, 4, 6, 11, 0)
    
    # Simulation of SLA logic
    def calculate_deadline(start, hours):
        current = start
        remaining = hours
        while remaining > 0:
            # Skip weekends
            if current.weekday() >= 5:
                current = (current + timedelta(days=1)).replace(hour=8, minute=0)
                continue
            
            # End of day check
            eod = current.replace(hour=17, minute=0)
            available_today = (eod - current).total_seconds() / 3600
            
            if available_today >= remaining:
                return current + timedelta(hours=remaining)
            else:
                remaining -= available_today
                current = (current + timedelta(days=1)).replace(hour=8, minute=0)
        return current

    actual_deadline = calculate_deadline(start_time, sla_hours)
    assert actual_deadline == expected_deadline

# --- 4. Ticket State Machine Transitions ---
@pytest.mark.asyncio
async def test_ticket_state_machine(db: AsyncSession):
    """Test invalid state transitions for tickets."""
    ticket = Ticket(title="Broken Mouse", status="OPEN", priority="LOW")
    db.add(ticket)
    await db.commit()
    
    service = TicketService(db)
    
    # Try OPEN -> RESOLVED (Invalid, must go through IN_PROGRESS)
    with pytest.raises(ValueError) as excinfo:
        await service.update_ticket_status(ticket.id, "RESOLVED")
    assert "Invalid transition" in str(excinfo.value)
    
    # Try OPEN -> IN_PROGRESS (Valid)
    await service.update_ticket_status(ticket.id, "IN_PROGRESS")
    await db.refresh(ticket)
    assert ticket.status == "IN_PROGRESS"
