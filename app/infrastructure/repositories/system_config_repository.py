from typing import Optional

from sqlalchemy.orm import Session

from app.domain.entities.system_config import SystemConfig
from app.domain.repositories.i_system_config_repository import ISystemConfigRepository
from app.infrastructure.orm.system_config import SystemConfigORM


class SqlSystemConfigRepository(ISystemConfigRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def find_by_key(self, key: str) -> Optional[SystemConfig]:
        orm = self._session.get(SystemConfigORM, key)
        if orm is None:
            return None
        return SystemConfig(key=orm.key, value=orm.value, description=orm.description)

    def find_all(self) -> list[SystemConfig]:
        rows = self._session.query(SystemConfigORM).order_by(SystemConfigORM.key).all()
        return [SystemConfig(key=r.key, value=r.value, description=r.description) for r in rows]

    def save_or_update(self, config: SystemConfig) -> SystemConfig:
        orm = self._session.get(SystemConfigORM, config.key)
        if orm is None:
            orm = SystemConfigORM(
                key=config.key,
                value=config.value,
                description=config.description,
            )
            self._session.add(orm)
        else:
            orm.value = config.value
            orm.description = config.description
        self._session.commit()
        self._session.refresh(orm)
        return SystemConfig(key=orm.key, value=orm.value, description=orm.description)
