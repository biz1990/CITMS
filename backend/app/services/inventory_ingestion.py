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
            device.last_reconciled_at = datetime.utcnow() # v3.6 §4.1
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
        """
        v3.6 §13.1: FULL_REPLACE STRATEGY & Regex Mapping.
        """
        from app.models.software import SoftwareCatalog, SoftwareInstallation
        import re

        # 1. Load Software Catalog for Regex mapping
        catalog_stmt = select(SoftwareCatalog).where(SoftwareCatalog.deleted_at.is_(None))
        catalog = (await self.db.execute(catalog_stmt)).scalars().all()

        # 2. Map reported software strings to Catalog IDs using regex
        mapped_reported = []
        for rep in reported_software:
            rep_name = rep["name"]
            matched_catalog_id = None
            for entry in catalog:
                if entry.regex_pattern and re.search(entry.regex_pattern, rep_name, re.IGNORECASE):
                    matched_catalog_id = entry.id
                    break
            mapped_reported.append({
                "raw_name": rep_name,
                "catalog_id": matched_catalog_id,
                "version": rep.get("version", "1.0")
            })

        # 3. Get currently installed software (Baseline for Diff)
        stmt = select(SoftwareInstallation).where(
            SoftwareInstallation.device_id == device_id,
            SoftwareInstallation.deleted_at.is_(None)
        )
        existing_sw = (await self.db.execute(stmt)).scalars().all()
        
        # Mapping for diffing: we use (catalog_id if exists else raw_name) as identity
        existing_map = { (sw.software_catalog_id or sw.software_name): sw for sw in existing_sw }
        reported_identities = { (m["catalog_id"] or m["raw_name"]) for m in mapped_reported }

        # 4. FULL_REPLACE: Soft-delete missing items
        for identity, sw_obj in existing_map.items():
            if identity not in reported_identities:
                sw_obj.deleted_at = datetime.utcnow()
                self.db.add(sw_obj)
                logger.info(f"Software {identity} removed from device {device_id} (FULL_REPLACE)")

        # 5. Insert new/updated items
        from app.services.license import LicenseService
        license_svc = LicenseService(self.db)

        for m in mapped_reported:
            identity = (m["catalog_id"] or m["raw_name"])
            if identity not in existing_map:
                sw_install = SoftwareInstallation(
                    device_id=device_id,
                    software_catalog_id=m["catalog_id"],
                    software_name=m["raw_name"],
                    version=m["version"],
                    install_date=datetime.utcnow()
                )
                self.db.add(sw_install)
                await self.db.flush()
                # Automated license assignment in v3.6
                await license_svc.assign_license(sw_install)
