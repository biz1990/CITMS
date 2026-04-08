from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Any, Dict
import uuid

class ProblemDetails(BaseModel):
    type: str
    title: str
    status: int
    detail: str
    instance: Optional[str] = None
    trace_id: Optional[str] = None
    request_id: Optional[str] = None
    extensions: Optional[Dict[str, Any]] = None

async def rfc7807_exception_handler(request: Request, exc: HTTPException):
    # If detail is already a dict (like our 409 conflict), use it
    if isinstance(exc.detail, dict):
        problem_data = exc.detail
    else:
        problem_data = {
            "type": f"https://citms.internal/errors/{exc.status_code}",
            "title": getattr(exc, "title", "An error occurred"),
            "status": exc.status_code,
            "detail": str(exc.detail),
        }

    # Ensure HTTP 500 has a standard title if not provided
    if exc.status_code == 500 and problem_data.get("title") == "An error occurred":
        problem_data["title"] = "Internal Server Error"

    problem = ProblemDetails(
        **problem_data,
        instance=str(request.url),
        trace_id=getattr(request.state, "trace_id", None),
        request_id=request.headers.get("X-Request-ID")
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=problem.model_dump(exclude_none=True)
    )
