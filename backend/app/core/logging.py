import logging
import sys
from pythonjsonlogger import jsonlogger
from .config import settings

def setup_logging():
    logger = logging.getLogger()
    
    # Remove all default handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    logHandler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(levelname)s %(name)s %(funcName)s %(message)s'
    )
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
    
    # Suppress verbose loggers from libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("alembic").setLevel(logging.INFO)
