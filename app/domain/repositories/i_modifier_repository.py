from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from app.domain.entities.modifier import Modifier


class IModifierRepository(ABC):
    @abstractmethod
    def save(self, modifier: Modifier) -> Modifier: ...

    @abstractmethod
    def find_by_id(self, modifier_id: UUID) -> Optional[Modifier]: ...

    @abstractmethod
    def find_by_product(self, product_id: UUID) -> list[Modifier]: ...

    @abstractmethod
    def update(self, modifier: Modifier) -> Modifier: ...

    @abstractmethod
    def delete(self, modifier_id: UUID) -> None:
        """Raises ModifierHasHistoryError if the modifier is referenced in any order."""
        ...
