from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from app.domain.entities.branch import Branch
from app.domain.exceptions import BranchNotFoundError
from app.domain.repositories.i_branch_repository import IBranchRepository


@dataclass
class UpdateBranchInput:
    branch_id: UUID
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None


class UpdateBranchUseCase:
    def __init__(self, branch_repo: IBranchRepository) -> None:
        self._branch_repo = branch_repo

    def execute(self, input_data: UpdateBranchInput) -> Branch:
        branch = self._branch_repo.find_by_id(input_data.branch_id)
        if branch is None:
            raise BranchNotFoundError(f"Branch {input_data.branch_id} not found")

        if input_data.name is not None:
            branch.name = input_data.name
        if input_data.address is not None:
            branch.address = input_data.address
        if input_data.phone is not None:
            branch.phone = input_data.phone

        return self._branch_repo.update(branch)
