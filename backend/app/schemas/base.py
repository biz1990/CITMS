from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel, ConfigDict

T = TypeVar("T")

class Pagination(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    size: int
    has_next: bool

class ErrorInstance(BaseModel):
    type: str
    title: str
    status: int
    detail: str
    instance: str
    trace_id: str
    
class GenericMessage(BaseModel):
    detail: str
