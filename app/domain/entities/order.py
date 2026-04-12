from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from app.domain.enums import OrderStatus, PaymentMethod, OrderItemStatus


@dataclass
class OrderItemModifier:
    id: UUID
    order_item_id: UUID
    modifier_id: UUID
    applied_extra_price: Decimal  # NUMERIC(12,4) — snapshot at order time


@dataclass
class OrderItem:
    id: UUID
    order_id: UUID
    product_id: UUID
    quantity: int
    unit_price: Decimal           # NUMERIC(12,4) — snapshot at order time
    applied_tax_rate: Decimal     # NUMERIC(5,4)  — snapshot at order time
    status: OrderItemStatus
    notes: Optional[str]
    modifiers: list[OrderItemModifier] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise ValueError(f"quantity must be > 0, got {self.quantity}")
        if self.unit_price < Decimal("0"):
            raise ValueError(f"unit_price must be >= 0, got {self.unit_price}")
        if not (Decimal("0") <= self.applied_tax_rate <= Decimal("1")):
            raise ValueError(
                f"applied_tax_rate must be in [0, 1], got {self.applied_tax_rate}"
            )

    @property
    def line_subtotal(self) -> Decimal:
        """unit_price * quantity (before tax)."""
        extra = sum(m.applied_extra_price for m in self.modifiers)
        return (self.unit_price + extra) * self.quantity

    @property
    def line_tax(self) -> Decimal:
        """Tax amount for this item."""
        return self.line_subtotal * self.applied_tax_rate


@dataclass
class OrderTable:
    order_id: UUID
    table_id: UUID
    joined_at: datetime


@dataclass
class Order:
    id: UUID
    user_id: UUID
    subtotal: Decimal       # NUMERIC(12,4)
    taxes: Decimal          # NUMERIC(12,4)
    tip: Decimal            # NUMERIC(12,4) default 0
    discount: Decimal       # NUMERIC(12,4) default 0
    total_amount: Decimal   # NUMERIC(12,4) = subtotal + taxes + tip - discount
    status: OrderStatus
    payment_method: Optional[PaymentMethod]
    created_at: datetime
    updated_at: datetime
    items: list[OrderItem] = field(default_factory=list)
    tables: list[OrderTable] = field(default_factory=list)

    def is_open(self) -> bool:
        return self.status == OrderStatus.OPEN

    def recalculate_totals(self) -> None:
        """Recalculates subtotal, taxes, and total_amount from active items."""
        active = [i for i in self.items if i.status != OrderItemStatus.CANCELLED]
        self.subtotal = sum(i.line_subtotal for i in active)
        self.taxes = sum(i.line_tax for i in active)
        self.total_amount = self.subtotal + self.taxes + self.tip - self.discount
