import logging
import sys
from pythonjsonlogger import jsonlogger
from .config import settings
from .audit_context import request_id

class ContextualJsonFormatter(jsonlogger.JsonFormatter):
    """
    v3.6 §9.3: Custom JSON formatter to automatically inject trace_id (request_id)
    from contextvars into every log entry.
    """
    def add_fields(self, log_record, record, message_dict):
        super(ContextualJsonFormatter, self).add_fields(log_record, record, message_dict)
        trace_id = request_id.get()
        if trace_id:
            log_record['trace_id'] = str(trace_id)
        if not log_record.get('timestamp'):
            from datetime import datetime
            log_record['timestamp'] = datetime.utcnow().isoformat()
        log_record['level'] = record.levelname
        log_record['module'] = record.name

def setup_logging():
    logger = logging.getLogger()
    
    # Remove all default handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    logHandler = logging.StreamHandler(sys.stdout)
    formatter = ContextualJsonFormatter(
        '%(asctime)s %(levelname)s %(name)s %(funcName)s %(message)s'
    )
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
    
    # Suppress verbose loggers from libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("alembic").setLevel(logging.INFO)
