from typing import Optional

from sqlalchemy import VARCHAR, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.infrastructure.orm.base import Base


class BranchORM(Base):
    __tablename__ = "branch"

    id: Mapped[str] = mapped_column(PG_UUID(as_uuid=False), primary_key=True)
    name: Mapped[str] = mapped_column(VARCHAR(150), nullable=False)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(VARCHAR(20), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
