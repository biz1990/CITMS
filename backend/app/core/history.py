import json
import uuid
from datetime import datetime
from typing import Any, Dict

from sqlalchemy import event, inspect
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workflow import HistoryLog
from app.core.audit_context import current_user_id, request_id

def get_model_changes(obj: Any) -> Dict[str, Any]:
    """
    Returns a dictionary of changed attributes: {attr: (old, new)}
    """
    state = inspect(obj)
    changes = {}
    for attr in state.mapper.column_attrs:
        hist = state.get_history(attr.key, True)
        if hist.has_changes():
            old_val = hist.deleted[0] if hist.deleted else None
            new_val = hist.added[0] if hist.added else None
            changes[attr.key] = {"old": old_val, "new": new_val}
    return changes

def _create_history_log(session: Session, obj: Any, action: str):
    user_id = current_user_id.get()
    req_id = request_id.get() or uuid.uuid4()
    
    changes = get_model_changes(obj)
    if not changes and action == "UPDATE":
        return

    old_values = {k: v["old"] for k, v in changes.items()} if action != "INSERT" else None
    new_values = {k: v["new"] for k, v in changes.items()} if action != "DELETE" else None
    
    # Handle non-serializable types for JSONB
    def serializer(v):
        if isinstance(v, (datetime, uuid.UUID)):
            return str(v)
        return v

    log = HistoryLog(
        id=uuid.uuid4(),
        created_at=datetime.utcnow(),
        table_name=obj.__tablename__,
        record_id=obj.id,
        action=action,
        old_value={k: serializer(v) for k, v in old_values.items()} if old_values else None,
        new_value={k: serializer(v) for k, v in new_values.items()} if new_values else None,
        changed_by_user_id=user_id,
        request_id=req_id
    )
    session.add(log)

def register_audit_listeners():
    """
    Registers SQLAlchemy listeners for automated audit logging.
    """
    from app.models.base import OptimisticLockMixin
    
    @event.listens_for(Session, "before_flush")
    def receive_before_flush(session, flush_context, instances):
        for obj in session.new:
            if hasattr(obj, "__tablename__"):
                _create_history_log(session, obj, "INSERT")
        
        for obj in session.dirty:
            if hasattr(obj, "__tablename__"):
                _create_history_log(session, obj, "UPDATE")
        
        for obj in session.deleted:
            if hasattr(obj, "__tablename__"):
                _create_history_log(session, obj, "DELETE")
