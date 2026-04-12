from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import VARCHAR, Boolean, DateTime, ForeignKey, Integer, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.infrastructure.orm.base import Base


class OrderORM(Base):
    __tablename__ = "order"

    id: Mapped[str] = mapped_column(PG_UUID(as_uuid=False), primary_key=True)
    user_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False), ForeignKey("user.id"), nullable=False
    )
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    taxes: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    tip: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False, default=Decimal("0"))
    discount: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False, default=Decimal("0"))
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    status: Mapped[str] = mapped_column(VARCHAR(50), nullable=False)
    payment_method: Mapped[Optional[str]] = mapped_column(VARCHAR(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class OrderTableORM(Base):
    __tablename__ = "order_table"

    order_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False), ForeignKey("order.id"), primary_key=True
    )
    table_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False), ForeignKey("restaurant_table.id"), primary_key=True
    )
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class OrderItemORM(Base):
    __tablename__ = "order_item"

    id: Mapped[str] = mapped_column(PG_UUID(as_uuid=False), primary_key=True)
    order_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False), ForeignKey("order.id"), nullable=False
    )
    product_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False), ForeignKey("product.id"), nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    applied_tax_rate: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    status: Mapped[str] = mapped_column(VARCHAR(50), nullable=False, default="PENDING")
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class OrderItemModifierORM(Base):
    __tablename__ = "order_item_modifier"

    id: Mapped[str] = mapped_column(PG_UUID(as_uuid=False), primary_key=True)
    order_item_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False), ForeignKey("order_item.id"), nullable=False
    )
    modifier_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False), ForeignKey("modifier.id"), nullable=False
    )
    applied_extra_price: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
