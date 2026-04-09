from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from app.domain.entities.product import Product


class IProductRepository(ABC):
    @abstractmethod
    def save(self, product: Product) -> Product: ...

    @abstractmethod
    def find_by_id(self, product_id: UUID) -> Optional[Product]: ...

    @abstractmethod
    def find_by_category(self, category_id: UUID) -> list[Product]: ...

    @abstractmethod
    def update(self, product: Product) -> Product: ...
