import uuid

from app.domain.entities.user import User
from app.domain.enums import RoleName
from app.infrastructure.orm.user import UserORM


def to_domain(orm: UserORM) -> User:
    return User(
        id=uuid.UUID(orm.id),
        role_id=uuid.UUID(orm.role_id),
        role_name=RoleName(orm.role.name),
        branch_id=uuid.UUID(orm.branch_id) if orm.branch_id else None,
        given_name=orm.given_name,
        paternal_surname=orm.paternal_surname,
        maternal_surname=orm.maternal_surname,
        email=orm.email,
        password_hash=orm.password_hash,
        pin_hash=orm.pin_hash,
        is_active=orm.is_active,
        created_at=orm.created_at,
    )


def to_orm(entity: User) -> UserORM:
    return UserORM(
        id=str(entity.id),
        role_id=str(entity.role_id),
        branch_id=str(entity.branch_id) if entity.branch_id else None,
        given_name=entity.given_name,
        paternal_surname=entity.paternal_surname,
        maternal_surname=entity.maternal_surname,
        email=entity.email,
        password_hash=entity.password_hash,
        pin_hash=entity.pin_hash,
        is_active=entity.is_active,
        created_at=entity.created_at,
    )
