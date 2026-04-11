from fastapi import Query
from pydantic import BaseModel
from typing import Optional, List, TypeVar, Generic

T = TypeVar("T")

class PaginationParams(BaseModel):
    page: int = 1
    limit: int = 100
    
    @property
    def skip(self) -> int:
        return (self.page - 1) * self.limit

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    limit: int

def get_pagination_params(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(100, ge=1, le=1000, description="Items per page")
) -> PaginationParams:
    return PaginationParams(page=page, limit=limit)
