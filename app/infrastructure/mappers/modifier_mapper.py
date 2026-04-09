import uuid

from app.domain.entities.modifier import Modifier
from app.infrastructure.orm.modifier import ModifierORM


def to_domain(orm: ModifierORM) -> Modifier:
    return Modifier(
        id=uuid.UUID(orm.id),
        product_id=uuid.UUID(orm.product_id),
        name=orm.name,
        extra_price=orm.extra_price,
    )


def to_orm(entity: Modifier) -> ModifierORM:
    return ModifierORM(
        id=str(entity.id),
        product_id=str(entity.product_id),
        name=entity.name,
        extra_price=entity.extra_price,
    )
