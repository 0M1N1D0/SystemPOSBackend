import uuid

from app.domain.entities.branch import Branch
from app.infrastructure.orm.branch import BranchORM


def to_domain(orm: BranchORM) -> Branch:
    return Branch(
        id=uuid.UUID(orm.id),
        name=orm.name,
        address=orm.address,
        phone=orm.phone,
        is_active=orm.is_active,
    )


def to_orm(entity: Branch) -> BranchORM:
    return BranchORM(
        id=str(entity.id),
        name=entity.name,
        address=entity.address,
        phone=entity.phone,
        is_active=entity.is_active,
    )
