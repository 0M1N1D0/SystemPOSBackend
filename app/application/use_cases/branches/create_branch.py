import uuid
from dataclasses import dataclass
from typing import Optional

from app.domain.entities.branch import Branch
from app.domain.repositories.i_branch_repository import IBranchRepository


@dataclass
class CreateBranchInput:
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None


class CreateBranchUseCase:
    def __init__(self, branch_repo: IBranchRepository) -> None:
        self._branch_repo = branch_repo

    def execute(self, input_data: CreateBranchInput) -> Branch:
        branch = Branch(
            id=uuid.uuid4(),
            name=input_data.name,
            address=input_data.address,
            phone=input_data.phone,
            is_active=True,
        )
        return self._branch_repo.save(branch)
