from datetime import datetime
from typing import Optional

from sqlalchemy import VARCHAR, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.infrastructure.orm.base import Base


class ReservationORM(Base):
    __tablename__ = "reservation"

    id: Mapped[str] = mapped_column(PG_UUID(as_uuid=False), primary_key=True)
    branch_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False), ForeignKey("branch.id"), nullable=False
    )
    created_by_user_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False), ForeignKey("user.id"), nullable=False
    )
    order_id: Mapped[Optional[str]] = mapped_column(
        PG_UUID(as_uuid=False), ForeignKey("order.id"), nullable=True
    )
    guest_name: Mapped[str] = mapped_column(VARCHAR(150), nullable=False)
    guest_phone: Mapped[Optional[str]] = mapped_column(VARCHAR(20), nullable=True)
    party_size: Mapped[int] = mapped_column(Integer, nullable=False)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=90)
    status: Mapped[str] = mapped_column(VARCHAR(50), nullable=False, default="CONFIRMED")
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class ReservationTableORM(Base):
    __tablename__ = "reservation_table"

    reservation_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False), ForeignKey("reservation.id"), primary_key=True
    )
    table_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False), ForeignKey("restaurant_table.id"), primary_key=True
    )
