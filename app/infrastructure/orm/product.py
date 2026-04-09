from decimal import Decimal
from typing import Optional

from sqlalchemy import VARCHAR, Boolean, Integer, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.infrastructure.orm.base import Base


class ProductORM(Base):
    __tablename__ = "product"

    id: Mapped[str] = mapped_column(PG_UUID(as_uuid=False), primary_key=True)
    category_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False), ForeignKey("category.id"), nullable=False
    )
    tax_rate_id: Mapped[Optional[str]] = mapped_column(
        PG_UUID(as_uuid=False), ForeignKey("tax_rate.id"), nullable=True
    )
    name: Mapped[str] = mapped_column(VARCHAR(150), nullable=False)
    base_price: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    sort_order: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
