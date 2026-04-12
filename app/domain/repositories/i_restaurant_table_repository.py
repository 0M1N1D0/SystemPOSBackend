from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from app.domain.entities.restaurant_table import RestaurantTable
from app.domain.enums import TableStatus


class IRestaurantTableRepository(ABC):
    @abstractmethod
    def save(self, table: RestaurantTable) -> RestaurantTable: ...

    @abstractmethod
    def find_by_id(self, table_id: UUID) -> Optional[RestaurantTable]: ...

    @abstractmethod
    def find_by_branch(self, branch_id: UUID) -> list[RestaurantTable]: ...

    @abstractmethod
    def find_by_ids(self, table_ids: list[UUID]) -> list[RestaurantTable]: ...

    @abstractmethod
    def update_status(self, table_id: UUID, status: TableStatus) -> None: ...

    @abstractmethod
    def update(self, table: RestaurantTable) -> RestaurantTable: ...
