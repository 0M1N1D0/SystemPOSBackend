from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from app.domain.entities.role import Role
from app.domain.enums import RoleName


class IRoleRepository(ABC):
    @abstractmethod
    def find_by_id(self, role_id: UUID) -> Optional[Role]: ...

    @abstractmethod
    def find_by_name(self, name: RoleName) -> Optional[Role]: ...

    @abstractmethod
    def find_all(self) -> list[Role]: ...
