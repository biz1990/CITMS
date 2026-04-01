from .base import Base
from .user import Role, UserRole, User, Department
from .location import Location
from .inventory import Vendor, SparePartInventory
from .procurement import PurchaseOrder, PurchaseItem, Contract
from .device import Device, DeviceComponent, DeviceConnection, CMDBRelationship
from .ticket import Ticket, TicketComment, MaintenanceLog
from .software import SoftwareLicense, SoftwareInstallation, SerialBlacklist, SoftwareBlacklist
from .workflow import DeviceAssignment, Notification, WorkflowRequest, ApprovalHistory, HistoryLog

# Expose models to Alembic metadata
__all__ = [
    "Base",
    "Role", "UserRole", "User", "Department",
    "Location",
    "Vendor", "SparePartInventory",
    "PurchaseOrder", "PurchaseItem", "Contract",
    "Device", "DeviceComponent", "DeviceConnection", "CMDBRelationship",
    "Ticket", "TicketComment", "MaintenanceLog",
    "SoftwareLicense", "SoftwareInstallation", "SerialBlacklist", "SoftwareBlacklist",
    "DeviceAssignment", "Notification", "WorkflowRequest", "ApprovalHistory", "HistoryLog"
]
