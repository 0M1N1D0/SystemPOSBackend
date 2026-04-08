from datetime import datetime
from typing import Optional

from sqlalchemy import VARCHAR, Boolean, CHAR, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, TIMESTAMP

from app.infrastructure.orm.base import Base
from app.infrastructure.orm.role import RoleORM
from app.infrastructure.orm.branch import BranchORM


class UserORM(Base):
    __tablename__ = "user"

    id: Mapped[str] = mapped_column(PG_UUID(as_uuid=False), primary_key=True)
    branch_id: Mapped[Optional[str]] = mapped_column(
        PG_UUID(as_uuid=False),
        ForeignKey("branch.id", ondelete="SET NULL"),
        nullable=True,
    )
    role_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False),
        ForeignKey("role.id", ondelete="RESTRICT"),
        nullable=False,
    )
    given_name: Mapped[str] = mapped_column(VARCHAR(150), nullable=False)
    paternal_surname: Mapped[str] = mapped_column(VARCHAR(150), nullable=False)
    maternal_surname: Mapped[Optional[str]] = mapped_column(VARCHAR(150), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(VARCHAR(255), nullable=True)
    password_hash: Mapped[Optional[str]] = mapped_column(CHAR(60), nullable=True)
    pin_hash: Mapped[str] = mapped_column(CHAR(60), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)

    role: Mapped[RoleORM] = relationship("RoleORM", lazy="joined")
    branch: Mapped[Optional[BranchORM]] = relationship("BranchORM", lazy="select")
