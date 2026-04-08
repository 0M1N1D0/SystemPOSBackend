from app.domain.entities.branch import Branch
from app.domain.repositories.i_branch_repository import IBranchRepository


class ListBranchesUseCase:
    def __init__(self, branch_repo: IBranchRepository) -> None:
        self._branch_repo = branch_repo

    def execute(self) -> list[Branch]:
        return self._branch_repo.find_all()
