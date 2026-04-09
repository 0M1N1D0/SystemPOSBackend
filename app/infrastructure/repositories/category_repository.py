from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.entities.category import Category
from app.domain.repositories.i_category_repository import ICategoryRepository
from app.infrastructure.mappers import category_mapper
from app.infrastructure.orm.category import CategoryORM


class SqlCategoryRepository(ICategoryRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, category: Category) -> Category:
        orm = category_mapper.to_orm(category)
        self._session.add(orm)
        self._session.commit()
        self._session.refresh(orm)
        return category_mapper.to_domain(orm)

    def find_by_id(self, category_id: UUID) -> Optional[Category]:
        orm = self._session.get(CategoryORM, str(category_id))
        return category_mapper.to_domain(orm) if orm else None

    def find_all(self) -> list[Category]:
        rows = (
            self._session.query(CategoryORM)
            .order_by(CategoryORM.sort_order.nulls_last(), CategoryORM.name)
            .all()
        )
        return [category_mapper.to_domain(r) for r in rows]

    def update(self, category: Category) -> Category:
        orm = self._session.get(CategoryORM, str(category.id))
        orm.name = category.name
        orm.description = category.description
        orm.sort_order = category.sort_order
        self._session.commit()
        self._session.refresh(orm)
        return category_mapper.to_domain(orm)
