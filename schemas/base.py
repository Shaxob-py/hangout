from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar('T')

class ResponseWrapper(BaseModel, Generic[T]):
     message: str
     data: T | None = None
     status_code: int

class PaginationResponse(Generic[T]):
    items: list[T]
    total: int
    page: int
    per_page: int