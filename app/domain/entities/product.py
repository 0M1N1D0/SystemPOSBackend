from dataclasses import dataclass
from decimal import Decimal
from typing import Optional
from uuid import UUID


@dataclass
class Product:
    id: UUID
    category_id: UUID
    name: str
    base_price: Decimal          # NUMERIC(12,4)
    is_available: bool
    sort_order: Optional[int]
    tax_rate_id: Optional[UUID]  # None → use default tax rate at order time

    def __post_init__(self) -> None:
        if self.base_price < Decimal("0"):
            raise ValueError(f"base_price must be >= 0, got {self.base_price}")
