import uuid
from dataclasses import dataclass
from typing import Optional

from app.domain.entities.restaurant_table import RestaurantTable
from app.domain.exceptions import RestaurantTableNotFoundError
from app.domain.repositories.i_restaurant_table_repository import IRestaurantTableRepository


@dataclass
class UpdateTableInput:
    table_id: uuid.UUID
    identifier: Optional[str] = None
    capacity: Optional[int] = None


class UpdateTableUseCase:
    def __init__(self, table_repo: IRestaurantTableRepository) -> None:
        self._table_repo = table_repo

    def execute(self, input_data: UpdateTableInput) -> RestaurantTable:
        table = self._table_repo.find_by_id(input_data.table_id)
        if table is None:
            raise RestaurantTableNotFoundError(f"Table {input_data.table_id} not found")

        if input_data.identifier is not None:
            table.identifier = input_data.identifier
        if input_data.capacity is not None:
            table.capacity = input_data.capacity

        return self._table_repo.update(table)
