import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from app.core import audit_context

class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 1. Initialize request-id (either from header or new)
        req_id_str = request.headers.get("X-Request-ID")
        try:
            req_id = uuid.UUID(req_id_str) if req_id_str else uuid.uuid4()
        except ValueError:
            req_id = uuid.uuid4()
            
        # 2. Extract user_id from state (set by Auth middleware)
        user_id = None
        if hasattr(request.state, "user") and request.state.user:
            user_id = request.state.user.id
            
        # 3. Set ContextVars for the duration of the request
        token_u = audit_context.current_user_id.set(user_id)
        token_r = audit_context.request_id.set(req_id)
        
        try:
            response = await call_next(request)
            # Ensure X-Request-ID is in response for observability
            response.headers["X-Request-ID"] = str(req_id)
            return response
        finally:
            # 4. Clean up ContextVars (important!)
            audit_context.current_user_id.reset(token_u)
            audit_context.request_id.reset(token_r)
