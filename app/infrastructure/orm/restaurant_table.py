from typing import Optional

from sqlalchemy import VARCHAR, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.infrastructure.orm.base import Base


class RestaurantTableORM(Base):
    __tablename__ = "restaurant_table"

    id: Mapped[str] = mapped_column(PG_UUID(as_uuid=False), primary_key=True)
    branch_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False),
        ForeignKey("branch.id", ondelete="RESTRICT"),
        nullable=False,
    )
    identifier: Mapped[str] = mapped_column(VARCHAR(50), nullable=False)
    capacity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(VARCHAR(50), nullable=False, default="FREE")
