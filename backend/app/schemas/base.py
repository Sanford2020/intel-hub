from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict

DataT = TypeVar("DataT")


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class TimestampSchema(BaseSchema):
    created_at: datetime
    updated_at: datetime


class APIResponse(BaseSchema, Generic[DataT]):
    success: bool = True
    data: DataT | None = None
    message: str = ""


class ErrorResponse(BaseSchema):
    success: bool = False
    error: dict[str, Any] = {}


class PaginatedResponse(BaseSchema, Generic[DataT]):
    success: bool = True
    data: list[DataT] = []
    total: int = 0
    page: int = 1
    page_size: int = 20
    total_pages: int = 0
