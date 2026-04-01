import pytest
import uuid
from app.services.asset import AssetService
from app.models.device import Device, DeviceConnection

@pytest.mark.asyncio
async def test_build_topology_hierarchy(db_session):
    # Setup test tree: Root -> Dock -> Scanner
    root = Device(id=uuid.uuid4(), serial_number="ROOT01", device_type="LAPTOP", status="IN_USE", version=1)
    dock = Device(id=uuid.uuid4(), serial_number="DOCK01", device_type="DOCKING_STATION", status="IN_USE", version=1)
    scanner = Device(id=uuid.uuid4(), serial_number="SCAN01", device_type="SCANNER", status="IN_USE", version=1)
    
    conn1 = DeviceConnection(id=uuid.uuid4(), source_device_id=root.id, target_device_id=dock.id, connection_type="USB")
    conn2 = DeviceConnection(id=uuid.uuid4(), source_device_id=dock.id, target_device_id=scanner.id, connection_type="SERIAL")
    
    db_session.add_all([root, dock, scanner, conn1, conn2])
    await db_session.commit()
    
    svc = AssetService(db_session)
    graph = await svc.build_topology_graph(root.id)
    
    # Validation
    assert "nodes" in graph
    assert "edges" in graph
    assert len(graph["nodes"]) == 3
    assert len(graph["edges"]) == 2
    
    # Check levels
    root_node = next(n for n in graph["nodes"] if n["id"] == str(root.id))
    assert root_node["level"] == 0
    
    scanner_node = next(n for n in graph["nodes"] if n["id"] == str(scanner.id))
    assert scanner_node["level"] == 2

@pytest.mark.asyncio
async def test_topology_cycle_prevention(db_session):
    # Setup cyclic connection: A -> B -> A
    dev_a = Device(id=uuid.uuid4(), serial_number="A", device_type="SERVER", version=1)
    dev_b = Device(id=uuid.uuid4(), serial_number="B", device_type="SERVER", version=1)
    
    conn1 = DeviceConnection(id=uuid.uuid4(), source_device_id=dev_a.id, target_device_id=dev_b.id, connection_type="TCP")
    conn2 = DeviceConnection(id=uuid.uuid4(), source_device_id=dev_b.id, target_device_id=dev_a.id, connection_type="TCP")
    
    db_session.add_all([dev_a, dev_b, conn1, conn2])
    await db_session.commit()
    
    # Building graph should NOT infinite-loop and just break the cycle
    svc = AssetService(db_session)
    graph = await svc.build_topology_graph(dev_a.id)
    assert len(graph["nodes"]) == 2
    
@pytest.mark.asyncio
async def test_device_not_found_topology(db_session):
    svc = AssetService(db_session)
    graph = await svc.build_topology_graph(uuid.uuid4())
    assert graph == {"nodes": [], "edges": []}
