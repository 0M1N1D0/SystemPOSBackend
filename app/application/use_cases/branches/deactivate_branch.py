from uuid import UUID

from app.domain.entities.branch import Branch
from app.domain.exceptions import BranchNotFoundError
from app.domain.repositories.i_branch_repository import IBranchRepository


class DeactivateBranchUseCase:
    def __init__(self, branch_repo: IBranchRepository) -> None:
        self._branch_repo = branch_repo

    def execute(self, branch_id: UUID) -> Branch:
        branch = self._branch_repo.find_by_id(branch_id)
        if branch is None:
            raise BranchNotFoundError(f"Branch {branch_id} not found")

        branch.is_active = False
        return self._branch_repo.update(branch)
