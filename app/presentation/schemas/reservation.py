from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.enums import ReservationStatus


class ReservationTableResponse(BaseModel):
    table_id: UUID


class ReservationResponse(BaseModel):
    id: UUID
    branch_id: UUID
    created_by_user_id: UUID
    order_id: Optional[UUID]
    guest_name: str
    guest_phone: Optional[str]
    party_size: int
    scheduled_at: datetime
    duration_minutes: int
    status: ReservationStatus
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    tables: list[ReservationTableResponse]


class CreateReservationRequest(BaseModel):
    branch_id: UUID
    created_by_user_id: UUID
    guest_name: str = Field(min_length=1, max_length=150)
    party_size: int = Field(ge=1)
    scheduled_at: datetime
    duration_minutes: int = Field(default=90, ge=1)
    table_ids: list[UUID] = Field(default_factory=list)
    guest_phone: Optional[str] = Field(default=None, max_length=20)
    notes: Optional[str] = None


class UpdateReservationRequest(BaseModel):
    guest_name: Optional[str] = Field(default=None, min_length=1, max_length=150)
    guest_phone: Optional[str] = Field(default=None, max_length=20)
    party_size: Optional[int] = Field(default=None, ge=1)
    scheduled_at: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(default=None, ge=1)
    notes: Optional[str] = None
    table_ids: Optional[list[UUID]] = None


class CancelReservationRequest(BaseModel):
    reason: Optional[str] = None
