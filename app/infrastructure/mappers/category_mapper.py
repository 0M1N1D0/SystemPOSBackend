import uuid

from app.domain.entities.category import Category
from app.infrastructure.orm.category import CategoryORM


def to_domain(orm: CategoryORM) -> Category:
    return Category(
        id=uuid.UUID(orm.id),
        name=orm.name,
        description=orm.description,
        sort_order=orm.sort_order,
    )


def to_orm(entity: Category) -> CategoryORM:
    return CategoryORM(
        id=str(entity.id),
        name=entity.name,
        description=entity.description,
        sort_order=entity.sort_order,
    )
