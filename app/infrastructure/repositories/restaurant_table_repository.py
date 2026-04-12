from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.entities.restaurant_table import RestaurantTable
from app.domain.enums import TableStatus
from app.domain.repositories.i_restaurant_table_repository import IRestaurantTableRepository
from app.infrastructure.mappers import restaurant_table_mapper
from app.infrastructure.orm.restaurant_table import RestaurantTableORM


class SqlRestaurantTableRepository(IRestaurantTableRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, table: RestaurantTable) -> RestaurantTable:
        orm = restaurant_table_mapper.to_orm(table)
        self._session.add(orm)
        self._session.commit()
        self._session.refresh(orm)
        return restaurant_table_mapper.to_domain(orm)

    def find_by_id(self, table_id: UUID) -> Optional[RestaurantTable]:
        orm = self._session.get(RestaurantTableORM, str(table_id))
        return restaurant_table_mapper.to_domain(orm) if orm else None

    def find_by_branch(self, branch_id: UUID) -> list[RestaurantTable]:
        rows = (
            self._session.query(RestaurantTableORM)
            .filter(RestaurantTableORM.branch_id == str(branch_id))
            .all()
        )
        return [restaurant_table_mapper.to_domain(r) for r in rows]

    def find_by_ids(self, table_ids: list[UUID]) -> list[RestaurantTable]:
        str_ids = [str(tid) for tid in table_ids]
        rows = (
            self._session.query(RestaurantTableORM)
            .filter(RestaurantTableORM.id.in_(str_ids))
            .all()
        )
        return [restaurant_table_mapper.to_domain(r) for r in rows]

    def update_status(self, table_id: UUID, status: TableStatus) -> None:
        orm = self._session.get(RestaurantTableORM, str(table_id))
        if orm:
            orm.status = status.value
            self._session.commit()

    def update(self, table: RestaurantTable) -> RestaurantTable:
        orm = self._session.get(RestaurantTableORM, str(table.id))
        orm.identifier = table.identifier
        orm.capacity = table.capacity
        orm.status = table.status.value
        self._session.commit()
        self._session.refresh(orm)
        return restaurant_table_mapper.to_domain(orm)
