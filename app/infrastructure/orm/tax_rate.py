from decimal import Decimal

from sqlalchemy import VARCHAR, Boolean, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.infrastructure.orm.base import Base


class TaxRateORM(Base):
    __tablename__ = "tax_rate"

    id: Mapped[str] = mapped_column(PG_UUID(as_uuid=False), primary_key=True)
    name: Mapped[str] = mapped_column(VARCHAR(100), nullable=False)
    rate: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
