from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    role_id: UUID
    given_name: str = Field(max_length=150)
    paternal_surname: str = Field(max_length=150)
    pin: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$")
    branch_id: Optional[UUID] = None
    maternal_surname: Optional[str] = Field(None, max_length=150)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)


class UserUpdate(BaseModel):
    given_name: Optional[str] = Field(None, max_length=150)
    paternal_surname: Optional[str] = Field(None, max_length=150)
    maternal_surname: Optional[str] = Field(None, max_length=150)
    branch_id: Optional[UUID] = None


class ChangePinRequest(BaseModel):
    current_pin: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$")
    new_pin: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$")


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)


class UserResponse(BaseModel):
    id: UUID
    role_id: UUID
    role_name: str
    branch_id: Optional[UUID]
    given_name: str
    paternal_surname: str
    maternal_surname: Optional[str]
    email: Optional[str]
    is_active: bool
    created_at: datetime
