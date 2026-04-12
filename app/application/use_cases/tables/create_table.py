import uuid
from dataclasses import dataclass
from typing import Optional

from app.domain.entities.restaurant_table import RestaurantTable
from app.domain.enums import TableStatus
from app.domain.exceptions import BranchNotFoundError
from app.domain.repositories.i_branch_repository import IBranchRepository
from app.domain.repositories.i_restaurant_table_repository import IRestaurantTableRepository


@dataclass
class CreateTableInput:
    branch_id: uuid.UUID
    identifier: str
    capacity: Optional[int] = None


class CreateTableUseCase:
    def __init__(
        self,
        table_repo: IRestaurantTableRepository,
        branch_repo: IBranchRepository,
    ) -> None:
        self._table_repo = table_repo
        self._branch_repo = branch_repo

    def execute(self, input_data: CreateTableInput) -> RestaurantTable:
        branch = self._branch_repo.find_by_id(input_data.branch_id)
        if branch is None:
            raise BranchNotFoundError(f"Branch {input_data.branch_id} not found")

        table = RestaurantTable(
            id=uuid.uuid4(),
            branch_id=input_data.branch_id,
            identifier=input_data.identifier,
            capacity=input_data.capacity,
            status=TableStatus.FREE,
        )
        return self._table_repo.save(table)
