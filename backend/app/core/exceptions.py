from fastapi import Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

class CITMSException(Exception):
    def __init__(self, status_code: int, title: str, detail: str, error_type: str = "general"):
        self.status_code = status_code
        self.title = title
        self.detail = detail
        # Error type URI compliant with RFC 7807
        self.type = f"https://citms.internal/errors/{error_type}"

async def citms_exception_handler(request: Request, exc: CITMSException):
    trace_id = getattr(request.state, "request_id", "unknown-trace")
    logger.error(f"[{trace_id}] {exc.title}: {exc.detail}")
    
    content = {
        "type": exc.type,
        "title": exc.title,
        "status": exc.status_code,
        "detail": exc.detail,
        "instance": request.url.path,
        "trace_id": trace_id
    }
    return JSONResponse(status_code=exc.status_code, content=content)

async def generic_exception_handler(request: Request, exc: Exception):
    trace_id = getattr(request.state, "request_id", "unknown-trace")
    logger.error(f"[{trace_id}] Unhandled Exception: {str(exc)}", exc_info=True)
    
    content = {
        "type": "https://citms.internal/errors/internal-server-error",
        "title": "Internal Server Error",
        "status": 500,
        "detail": "An unexpected error occurred.",
        "instance": request.url.path,
        "trace_id": trace_id
    }
    return JSONResponse(status_code=500, content=content)
    
class OptimisticLockException(CITMSException):
    def __init__(self):
        super().__init__(
            status_code=409,
            title="Xung đột cập nhật dữ liệu",
            detail="Tài liệu này đã bị người khác chỉnh sửa trước đó. Vui lòng tải lại trang để xem thay đổi mới nhất.",
            error_type="optimistic-lock-conflict"
        )
