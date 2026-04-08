from typing import Optional
from uuid import UUID

from app.domain.entities.user import User
from app.domain.repositories.i_user_repository import IUserRepository


class ListUsersUseCase:
    def __init__(self, user_repo: IUserRepository) -> None:
        self._user_repo = user_repo

    def execute(self, branch_id: Optional[UUID] = None) -> list[User]:
        if branch_id is not None:
            return self._user_repo.find_all_by_branch(branch_id)
        return self._user_repo.find_all()
