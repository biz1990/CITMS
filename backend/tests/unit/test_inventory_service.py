import pytest
import uuid
from app.services.inventory_ingestion import InventoryIngestionService
from app.models.device import Device
from sqlalchemy import select

@pytest.mark.asyncio
async def test_reconcile_happy_path(db_session):
    svc = InventoryIngestionService(db_session)
    payload = {
        "devices": [
            {
                "serial_number": "NEW-LAP-001",
                "device_type": "LAPTOP",
                "mac": "00:11:22:33:44:55",
                "connections": []
            }
        ]
    }
    await svc.process_report("run_01", payload)
    
    res = (await db_session.execute(select(Device).where(Device.serial_number=="NEW-LAP-001"))).scalars().first()
    assert res is not None
    assert res.device_type == "LAPTOP"

@pytest.mark.asyncio
async def test_reconcile_hybrid_docking_edge_case(db_session):
    svc = InventoryIngestionService(db_session)
    payload_complex = {
        "devices": [
            {
                "serial_number": "DOCK-ZEBRA",
                "device_type": "DOCKING_STATION",
                "connections": [{"type": "SERIAL", "target_serial": "SCANNER-ZEBRA"}]
            },
            {
                "serial_number": "SCANNER-ZEBRA",
                "device_type": "SCANNER",
                "connections": []
            }
        ]
    }
    await svc.process_report("run_02", payload_complex)
    
    dock = (await db_session.execute(select(Device).where(Device.serial_number=="DOCK-ZEBRA"))).scalars().first()
    scan = (await db_session.execute(select(Device).where(Device.serial_number=="SCANNER-ZEBRA"))).scalars().first()
    assert dock is not None
    assert scan is not None
