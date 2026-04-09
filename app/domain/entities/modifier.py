from dataclasses import dataclass, field
from decimal import Decimal
from uuid import UUID


@dataclass
class Modifier:
    id: UUID
    product_id: UUID
    name: str
    extra_price: Decimal = field(default=Decimal("0.0"))  # NUMERIC(12,4)

    def __post_init__(self) -> None:
        if self.extra_price < Decimal("0"):
            raise ValueError(f"extra_price must be >= 0, got {self.extra_price}")
