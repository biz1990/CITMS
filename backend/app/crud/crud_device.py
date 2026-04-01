from pydantic import BaseModel

class DeviceCreate(BaseModel):
    name: str

class DeviceUpdate(BaseModel):
    name: str

from .base import CRUDBase
from app.models.device import Device

class CRUDDevice(CRUDBase[Device, DeviceCreate, DeviceUpdate]):
    # Extends CRUDBase with specific methods for device (e.g. reconcile, etc.)
    pass

device = CRUDDevice(Device)
