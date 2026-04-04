import contextvars
import uuid
from typing import Optional

# Context variables to track the actor and request across async tasks
current_user_id: contextvars.ContextVar[Optional[uuid.UUID]] = contextvars.ContextVar("current_user_id", default=None)
request_id: contextvars.ContextVar[Optional[uuid.UUID]] = contextvars.ContextVar("request_id", default=None)

def set_audit_context(user_id: Optional[uuid.UUID], req_id: Optional[uuid.UUID]):
    current_user_id.set(user_id)
    request_id.set(req_id)

def get_audit_context():
    return current_user_id.get(), request_id.get()
