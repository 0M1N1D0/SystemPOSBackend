import uuid

from app.domain.entities.restaurant_table import RestaurantTable
from app.domain.enums import TableStatus
from app.infrastructure.orm.restaurant_table import RestaurantTableORM


def to_domain(orm: RestaurantTableORM) -> RestaurantTable:
    return RestaurantTable(
        id=uuid.UUID(orm.id),
        branch_id=uuid.UUID(orm.branch_id),
        identifier=orm.identifier,
        capacity=orm.capacity,
        status=TableStatus(orm.status),
    )


def to_orm(entity: RestaurantTable) -> RestaurantTableORM:
    return RestaurantTableORM(
        id=str(entity.id),
        branch_id=str(entity.branch_id),
        identifier=entity.identifier,
        capacity=entity.capacity,
        status=entity.status.value,
    )
