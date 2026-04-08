from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class BranchCreate(BaseModel):
    name: str = Field(max_length=150)
    address: Optional[str] = None
    phone: Optional[str] = Field(None, max_length=20)


class BranchUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=150)
    address: Optional[str] = None
    phone: Optional[str] = Field(None, max_length=20)


class BranchResponse(BaseModel):
    id: UUID
    name: str
    address: Optional[str]
    phone: Optional[str]
    is_active: bool
