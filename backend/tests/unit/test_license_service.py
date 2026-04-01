import pytest
import uuid
from sqlalchemy import select
from app.services.license import LicenseService
from app.models.software import SoftwareLicense, SoftwareInstallation

@pytest.mark.asyncio
async def test_license_used_seats_reconciliation(db_session):
    lic = SoftwareLicense(id=uuid.uuid4(), software_name="Visio", total_seats=10, used_seats=0)
    db_session.add(lic)
    await db_session.commit()
    
    svc = LicenseService(db_session)
    inst = SoftwareInstallation(id=uuid.uuid4(), license_id=lic.id, device_id=uuid.uuid4(), software_name="Visio", version="1")
    db_session.add(inst)
    await db_session.commit()
    
    await svc.check_compliance(lic.id)
    updated_lic = (await db_session.execute(select(SoftwareLicense).where(SoftwareLicense.id==lic.id))).scalars().first()
    assert updated_lic.used_seats == 1

@pytest.mark.asyncio
async def test_license_violation_pubsub_negative_flow(db_session, monkeypatch):
    lic = SoftwareLicense(id=uuid.uuid4(), software_name="Office", total_seats=1, used_seats=0)
    db_session.add(lic)
    await db_session.commit()
    
    inst1 = SoftwareInstallation(id=uuid.uuid4(), license_id=lic.id, device_id=uuid.uuid4(), software_name="Office", version="1")
    inst2 = SoftwareInstallation(id=uuid.uuid4(), license_id=lic.id, device_id=uuid.uuid4(), software_name="Office", version="1")
    db_session.add_all([inst1, inst2])
    await db_session.commit()
    
    svc = LicenseService(db_session)
    pub_sub_called = []
    
    async def mock_publish(event_type, payload):
        pub_sub_called.append((event_type, payload))
        
    from app.core.events import EventPublisher
    monkeypatch.setattr(EventPublisher, "publish_event", mock_publish)
    
    await svc.check_compliance(lic.id)
    assert len(pub_sub_called) == 1
    assert pub_sub_called[0][0] == "LICENSE_VIOLATION"
