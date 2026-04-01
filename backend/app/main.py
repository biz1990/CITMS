import uuid
import time
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError

from app.core.config import settings
from app.api.routers import api_router
from app.core.exceptions import CITMSException, citms_exception_handler, generic_exception_handler, OptimisticLockException

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Exception Handlers (RFC 7807)
app.add_exception_handler(CITMSException, citms_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Custom Middlewares
@app.middleware("http")
async def x_request_id_and_rate_limit(request: Request, call_next):
    # 1. Inject Request ID
    req_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = req_id
    
    # 2. Rate Limiting Mock (In real world use slowapi or redis ratelimiter here)
    # Simple IP throttle proxy pattern
    client_ip = request.client.host if request.client else "unknown"
    # redis_client.incr(client_ip) ... check limit
    
    # 3. Add to response
    start_time = time.time()
    try:
        response: Response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Request-ID"] = req_id
        return response
    except IntegrityError as e:
        # DB Error Mapping
        if "version" in str(e).lower():
            raise OptimisticLockException()
        raise CITMSException(400, "Database Error", str(e.orig), "db-error")
        
# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)
