import uuid

from app.domain.entities.restaurant_table import RestaurantTable
from app.domain.exceptions import RestaurantTableNotFoundError
from app.domain.repositories.i_restaurant_table_repository import IRestaurantTableRepository


class GetTableUseCase:
    def __init__(self, table_repo: IRestaurantTableRepository) -> None:
        self._table_repo = table_repo

    def execute(self, table_id: uuid.UUID) -> RestaurantTable:
        table = self._table_repo.find_by_id(table_id)
        if table is None:
            raise RestaurantTableNotFoundError(f"Table {table_id} not found")
        return table
