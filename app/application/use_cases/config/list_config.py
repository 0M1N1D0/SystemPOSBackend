from app.domain.entities.system_config import SystemConfig
from app.domain.repositories.i_system_config_repository import ISystemConfigRepository


class ListConfigUseCase:
    def __init__(self, config_repo: ISystemConfigRepository) -> None:
        self._config_repo = config_repo

    def execute(self) -> list[SystemConfig]:
        return self._config_repo.find_all()
