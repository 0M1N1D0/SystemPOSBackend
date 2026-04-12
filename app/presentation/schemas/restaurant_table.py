from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.enums import TableStatus


class TableCreate(BaseModel):
    branch_id: UUID
    identifier: str = Field(max_length=50)
    capacity: Optional[int] = Field(None, gt=0)


class TableUpdate(BaseModel):
    identifier: Optional[str] = Field(None, max_length=50)
    capacity: Optional[int] = Field(None, gt=0)


class TableResponse(BaseModel):
    id: UUID
    branch_id: UUID
    identifier: str
    capacity: Optional[int]
    status: TableStatus
