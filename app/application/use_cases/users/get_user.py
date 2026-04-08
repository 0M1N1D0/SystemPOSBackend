from uuid import UUID

from app.domain.entities.user import User
from app.domain.exceptions import UserNotFoundError
from app.domain.repositories.i_user_repository import IUserRepository


class GetUserUseCase:
    def __init__(self, user_repo: IUserRepository) -> None:
        self._user_repo = user_repo

    def execute(self, user_id: UUID) -> User:
        user = self._user_repo.find_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"User {user_id} not found")
        return user
