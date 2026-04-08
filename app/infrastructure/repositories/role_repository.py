from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.entities.role import Role
from app.domain.enums import RoleName
from app.domain.repositories.i_role_repository import IRoleRepository
from app.infrastructure.mappers import role_mapper
from app.infrastructure.orm.role import RoleORM


class SqlRoleRepository(IRoleRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def find_by_id(self, role_id: UUID) -> Optional[Role]:
        orm = self._session.get(RoleORM, str(role_id))
        return role_mapper.to_domain(orm) if orm else None

    def find_by_name(self, name: RoleName) -> Optional[Role]:
        orm = self._session.query(RoleORM).filter_by(name=name.value).first()
        return role_mapper.to_domain(orm) if orm else None

    def find_all(self) -> list[Role]:
        rows = self._session.query(RoleORM).all()
        return [role_mapper.to_domain(r) for r in rows]
