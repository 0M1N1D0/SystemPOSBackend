from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass
class TaxRate:
    id: UUID
    name: str
    rate: Decimal          # NUMERIC(5,4) — e.g. 0.1600 = 16%
    is_default: bool
    is_active: bool

    def __post_init__(self) -> None:
        if not (Decimal("0") <= self.rate <= Decimal("1")):
            raise ValueError(f"rate must be in [0.0000, 1.0000], got {self.rate}")
