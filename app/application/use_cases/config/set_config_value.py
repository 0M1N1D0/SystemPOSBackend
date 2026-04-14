from dataclasses import dataclass
from typing import Optional

from app.domain.entities.system_config import SystemConfig
from app.domain.repositories.i_system_config_repository import ISystemConfigRepository


@dataclass
class SetConfigValueInput:
    key: str
    value: str
    description: Optional[str] = None


class SetConfigValueUseCase:
    def __init__(self, config_repo: ISystemConfigRepository) -> None:
        self._config_repo = config_repo

    def execute(self, input_data: SetConfigValueInput) -> SystemConfig:
        config = SystemConfig(
            key=input_data.key,
            value=input_data.value,
            description=input_data.description,
        )
        return self._config_repo.save_or_update(config)
