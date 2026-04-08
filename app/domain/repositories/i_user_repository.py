from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from app.domain.entities.user import User


class IUserRepository(ABC):
    @abstractmethod
    def save(self, user: User) -> User: ...

    @abstractmethod
    def find_by_id(self, user_id: UUID) -> Optional[User]: ...

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]: ...

    @abstractmethod
    def find_all(self) -> list[User]: ...

    @abstractmethod
    def find_all_by_branch(self, branch_id: UUID) -> list[User]: ...

    @abstractmethod
    def update(self, user: User) -> User: ...
