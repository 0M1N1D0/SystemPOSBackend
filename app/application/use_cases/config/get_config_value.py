from app.domain.entities.system_config import SystemConfig
from app.domain.exceptions import SystemConfigNotFoundError
from app.domain.repositories.i_system_config_repository import ISystemConfigRepository


class GetConfigValueUseCase:
    def __init__(self, config_repo: ISystemConfigRepository) -> None:
        self._config_repo = config_repo

    def execute(self, key: str) -> SystemConfig:
        config = self._config_repo.find_by_key(key)
        if config is None:
            raise SystemConfigNotFoundError(f"Config key '{key}' not found")
        return config
