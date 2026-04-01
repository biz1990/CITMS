import uuid
import logging
from typing import Dict, Any, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.device import Device, DeviceConnection
from app.models.software import SoftwareInstallation

logger = logging.getLogger(__name__)

class InventoryIngestionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def process_report(self, run_id: str, payload: Dict[str, Any]):
        # Idempotency cache check omitted for brevity
        devices_data = payload.get("devices", [])
        for dev_data in devices_data:
            await self._process_device(dev_data)
        
        await self.db.commit()

    async def _process_device(self, data: Dict[str, Any]):
        mac = data.get("primary_mac")
        dock_serial = data.get("dock_serial")
        com_port = data.get("com_port")
        usb_connected = data.get("usb_connected", False)
        
        # Zebra / Hybrid Logic Decision
        device_subtype = "STANDARD"
        if dock_serial:
            device_subtype = "WIRELESS"
        elif com_port and usb_connected:
            device_subtype = "HYBRID"
        elif com_port:
            device_subtype = "COM"

        asset_tag = data.get("asset_tag")
        uuid_str = data.get("uuid_str")
        serial = data.get("serial_number")

        device = None
        for condition in [
            (Device.asset_tag == asset_tag) if asset_tag else None,
            (Device.uuid_str == uuid_str) if uuid_str else None,
            (Device.primary_mac == mac) if mac else None,
            (Device.serial_number == serial) if serial else None
        ]:
            if condition is not None:
                stmt = select(Device).where(condition)
                device = (await self.db.execute(stmt)).scalars().first()
                if device:
                    break

        if not device:
            new_id = uuid.uuid4()
            device = Device(
                id=new_id,
                uuid_str=str(new_id),
                serial_number=data.get("serial_number"),
                primary_mac=mac,
                device_type=data.get("device_type", "UNKNOWN"),
                device_subtype=device_subtype,
                status="IN_USE",
                last_seen=datetime.utcnow()
            )
            self.db.add(device)
            await self.db.flush()
        else:
            device.last_seen = datetime.utcnow()
            device.device_subtype = device_subtype

        # 1. Zebra Multi-docking
        if dock_serial:
            await self._upsert_dock_connection(device.id, dock_serial)
            
        # 2. COM/HYBRID Port
        if com_port:
            await self._upsert_com_connection(device.id, com_port, is_hybrid=usb_connected)
            
        # 3. License Tracking
        await self._reconcile_software(device.id, data.get("software", []))

    async def _upsert_dock_connection(self, scanner_id: uuid.UUID, dock_serial: str):
        stmt = select(Device).where(Device.serial_number == dock_serial, Device.device_subtype == 'DOCK')
        dock = (await self.db.execute(stmt)).scalars().first()
        if not dock:
            dock_id = uuid.uuid4()
            dock = Device(
                id=dock_id,
                serial_number=dock_serial,
                device_type="NETWORK_DEVICE",
                device_subtype="DOCK",
                status="IN_USE"
            )
            self.db.add(dock)
            await self.db.flush()
            
        stmt_conn = select(DeviceConnection).where(
            DeviceConnection.source_device_id == scanner_id,
            DeviceConnection.target_device_id == dock.id,
            DeviceConnection.connection_type == "DOCK_PAIRING"
        )
        conn = (await self.db.execute(stmt_conn)).scalars().first()
        if not conn:
            new_conn = DeviceConnection(
                source_device_id=scanner_id,
                target_device_id=dock.id,
                connection_type="DOCK_PAIRING",
                connected_at=datetime.utcnow()
            )
            self.db.add(new_conn)

    async def _upsert_com_connection(self, device_id: uuid.UUID, com_port: str, is_hybrid: bool = False):
        conn = DeviceConnection(
            source_device_id=device_id,
            target_device_id=device_id,
            connection_type="COM",
            port_name=com_port,
            connected_at=datetime.utcnow()
        )
        self.db.add(conn)
        if is_hybrid:
            conn_usb = DeviceConnection(
                source_device_id=device_id,
                target_device_id=device_id,
                connection_type="USB",
                connected_at=datetime.utcnow()
            )
            self.db.add(conn_usb)

    async def _reconcile_software(self, device_id: uuid.UUID, reported_software: List[Dict[str, Any]]):
        stmt = select(SoftwareInstallation).where(
            SoftwareInstallation.device_id == device_id,
            SoftwareInstallation.deleted_at.is_(None)
        )
        existing_sw = (await self.db.execute(stmt)).scalars().all()
        existing_names = {sw.software_name for sw in existing_sw}
        reported_names = {sw["name"] for sw in reported_software}
        
        # Uninstall trigger check (Soft Delete means DB trigger decreases used_seats)
        for installed in existing_sw:
            if installed.software_name not in reported_names:
                installed.deleted_at = datetime.utcnow()
                self.db.add(installed)
                logger.info(f"Software {installed.software_name} reported missing. Trigger will reduce used_seats automagically.")
                
        # Install trigger check
        from app.services.license import LicenseService
        license_svc = LicenseService(self.db)
        
        for rep_sw in reported_software:
            if rep_sw["name"] not in existing_names:
                sw_install = SoftwareInstallation(
                    device_id=device_id,
                    software_name=rep_sw["name"],
                    version=rep_sw.get("version", "1.0"),
                    install_date=datetime.utcnow()
                )
                self.db.add(sw_install)
                await self.db.flush()
                # Run the license assignment and potential violation publication
                await license_svc.assign_license(sw_install)
