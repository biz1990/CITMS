import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import logging

logger = logging.getLogger(__name__)

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID")
        if not request_id:
            request_id = str(uuid.uuid4())
            
        request.state.request_id = request_id
        
        # Add request_id to structured logs implicitly or manually later
        logger.info(f"Incoming request {request.method} {request.url}", extra={"request_id": request_id})
        
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
