from pydantic import BaseModel

class TicketCreate(BaseModel):
    title: str

class TicketUpdate(BaseModel):
    title: str

from .base import CRUDBase
from app.models.ticket import Ticket

class CRUDTicket(CRUDBase[Ticket, TicketCreate, TicketUpdate]):
    pass

ticket = CRUDTicket(Ticket)
