from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from app.domain.entities.category import Category


class ICategoryRepository(ABC):
    @abstractmethod
    def save(self, category: Category) -> Category: ...

    @abstractmethod
    def find_by_id(self, category_id: UUID) -> Optional[Category]: ...

    @abstractmethod
    def find_all(self) -> list[Category]: ...

    @abstractmethod
    def update(self, category: Category) -> Category: ...
