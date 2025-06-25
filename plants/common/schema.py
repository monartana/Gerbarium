from datetime import datetime
from http import HTTPStatus

from typing import Optional, Any
from pydantic import BaseModel


class OrmBase(BaseModel):
    class Config:
        from_attributes = True


class ApiResponse(OrmBase):
    data: Optional[Any] = None
    status: HTTPStatus = HTTPStatus.OK
    error: Optional[str] = None


class TimestampMixin(OrmBase):
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
