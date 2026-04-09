from decimal import Decimal

from sqlalchemy import VARCHAR, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.infrastructure.orm.base import Base


class ModifierORM(Base):
    __tablename__ = "modifier"

    id: Mapped[str] = mapped_column(PG_UUID(as_uuid=False), primary_key=True)
    product_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False), ForeignKey("product.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(VARCHAR(150), nullable=False)
    extra_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 4), nullable=False, default=Decimal("0.0")
    )
