import uuid

from app.domain.entities.role import Role
from app.domain.enums import RoleName
from app.infrastructure.orm.role import RoleORM


def to_domain(orm: RoleORM) -> Role:
    return Role(id=uuid.UUID(orm.id), name=RoleName(orm.name))


def to_orm(entity: Role) -> RoleORM:
    return RoleORM(id=str(entity.id), name=entity.name.value)
