from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from app.domain.entities.tax_rate import TaxRate


class ITaxRateRepository(ABC):
    @abstractmethod
    def save(self, tax_rate: TaxRate) -> TaxRate: ...

    @abstractmethod
    def find_by_id(self, tax_rate_id: UUID) -> Optional[TaxRate]: ...

    @abstractmethod
    def find_default(self) -> Optional[TaxRate]: ...

    @abstractmethod
    def find_all(self) -> list[TaxRate]: ...

    @abstractmethod
    def update(self, tax_rate: TaxRate) -> TaxRate: ...

    @abstractmethod
    def clear_default(self) -> None:
        """Sets is_default=False on every row that currently has is_default=True."""
        ...
