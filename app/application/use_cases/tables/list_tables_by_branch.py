import uuid

from app.domain.entities.restaurant_table import RestaurantTable
from app.domain.exceptions import BranchNotFoundError
from app.domain.repositories.i_branch_repository import IBranchRepository
from app.domain.repositories.i_restaurant_table_repository import IRestaurantTableRepository


class ListTablesByBranchUseCase:
    def __init__(
        self,
        table_repo: IRestaurantTableRepository,
        branch_repo: IBranchRepository,
    ) -> None:
        self._table_repo = table_repo
        self._branch_repo = branch_repo

    def execute(self, branch_id: uuid.UUID) -> list[RestaurantTable]:
        branch = self._branch_repo.find_by_id(branch_id)
        if branch is None:
            raise BranchNotFoundError(f"Branch {branch_id} not found")
        return self._table_repo.find_by_branch(branch_id)
