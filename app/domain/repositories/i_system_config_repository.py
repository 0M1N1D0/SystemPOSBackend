from abc import ABC, abstractmethod
from typing import Optional

from app.domain.entities.system_config import SystemConfig


class ISystemConfigRepository(ABC):

    @abstractmethod
    def find_by_key(self, key: str) -> Optional[SystemConfig]: ...

    @abstractmethod
    def find_all(self) -> list[SystemConfig]: ...

    @abstractmethod
    def save_or_update(self, config: SystemConfig) -> SystemConfig: ...
