from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from app.domain.entities.branch import Branch


class IBranchRepository(ABC):
    @abstractmethod
    def save(self, branch: Branch) -> Branch: ...

    @abstractmethod
    def find_by_id(self, branch_id: UUID) -> Optional[Branch]: ...

    @abstractmethod
    def find_all(self) -> list[Branch]: ...

    @abstractmethod
    def update(self, branch: Branch) -> Branch: ...
