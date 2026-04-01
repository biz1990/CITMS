import pytest
import uuid
from app.services.workflow import WorkflowService
from app.models.workflow import WorkflowRequest, DeviceAssignment
from app.models.device import Device
from sqlalchemy import select

@pytest.mark.asyncio
async def test_workflow_onboarding_success(db_session):
    svc = WorkflowService(db_session)
    dev = Device(id=uuid.uuid4(), serial_number="ASSET-TO-ASSIGN", device_type="LAPTOP", status="AVAILABLE", version=1)
    db_session.add(dev)
    await db_session.commit()
    
    target_user = uuid.uuid4()
    req = WorkflowRequest(id=uuid.uuid4(), workflow_type="ONBOARDING", status="PENDING", created_by=uuid.uuid4(), target_user_id=target_user, template_details={"device_id": str(dev.id)})
    db_session.add(req)
    await db_session.commit()
    
    # Execute onboarding
    await svc.execute_onboarding(req.id)
    
    # Verify Device Status changed
    await db_session.refresh(dev)
    assert dev.status == "IN_USE"
    
    # Verify Assignment created
    assign = (await db_session.execute(select(DeviceAssignment).where(DeviceAssignment.device_id==dev.id))).scalars().first()
    assert assign is not None
    assert assign.user_id == target_user

@pytest.mark.asyncio
async def test_workflow_offboarding_reclaims_devices(db_session):
    svc = WorkflowService(db_session)
    target_user = uuid.uuid4()
    dev = Device(id=uuid.uuid4(), serial_number="ASSET-RETURN", device_type="LAPTOP", status="IN_USE", version=1)
    db_session.add(dev)
    
    assign = DeviceAssignment(id=uuid.uuid4(), device_id=dev.id, user_id=target_user, assignment_type="PERMANENT")
    db_session.add(assign)
    await db_session.commit()
    
    # Execute offboarding
    recovered = await svc.execute_offboarding(target_user)
    
    assert recovered == 1
    await db_session.refresh(dev)
    assert dev.status == "AVAILABLE"
    
    await db_session.refresh(assign)
    assert assign.returned_at is not None
