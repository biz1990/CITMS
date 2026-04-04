import uuid
from typing import Any, Dict, Optional, Union
from sqlalchemy.ext.asyncio import AsyncSession

from .base import CRUDBase
from app.models.device import Device
from app.schemas.device import DeviceCreate, DeviceUpdate
from app.core.security import AES256GCMHelper

class CRUDDevice(CRUDBase[Device, DeviceCreate, DeviceUpdate]):
    async def create(self, db: AsyncSession, *, obj_in: DeviceCreate) -> Device:
        obj_in_data = obj_in.model_dump()
        
        # Module 2: Encrypt RustDesk password if present
        if obj_in_data.get("rustdesk_password"):
            pwd = obj_in_data.pop("rustdesk_password")
            obj_in_data["rustdesk_password_enc"] = AES256GCMHelper.encrypt(pwd)
            
        db_obj = Device(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, db: AsyncSession, *, db_obj: Device, obj_in: Union[DeviceUpdate, Dict[str, Any]]
    ) -> Device:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
            
        # Module 2: Encrypt RustDesk password if being updated
        if "rustdesk_password" in update_data:
            pwd = update_data.pop("rustdesk_password")
            if pwd:
                update_data["rustdesk_password_enc"] = AES256GCMHelper.encrypt(pwd)
            else:
                update_data["rustdesk_password_enc"] = None
                
        return await super().update(db, db_obj=db_obj, obj_in=update_data)

device = CRUDDevice(Device)
