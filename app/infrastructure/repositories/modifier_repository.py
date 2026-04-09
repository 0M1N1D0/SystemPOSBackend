from typing import Optional
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.domain.entities.modifier import Modifier
from app.domain.exceptions import ModifierHasHistoryError
from app.domain.repositories.i_modifier_repository import IModifierRepository
from app.infrastructure.mappers import modifier_mapper
from app.infrastructure.orm.modifier import ModifierORM


class SqlModifierRepository(IModifierRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, modifier: Modifier) -> Modifier:
        orm = modifier_mapper.to_orm(modifier)
        self._session.add(orm)
        self._session.commit()
        self._session.refresh(orm)
        return modifier_mapper.to_domain(orm)

    def find_by_id(self, modifier_id: UUID) -> Optional[Modifier]:
        orm = self._session.get(ModifierORM, str(modifier_id))
        return modifier_mapper.to_domain(orm) if orm else None

    def find_by_product(self, product_id: UUID) -> list[Modifier]:
        rows = (
            self._session.query(ModifierORM)
            .filter(ModifierORM.product_id == str(product_id))
            .order_by(ModifierORM.name)
            .all()
        )
        return [modifier_mapper.to_domain(r) for r in rows]

    def update(self, modifier: Modifier) -> Modifier:
        orm = self._session.get(ModifierORM, str(modifier.id))
        orm.name = modifier.name
        orm.extra_price = modifier.extra_price
        self._session.commit()
        self._session.refresh(orm)
        return modifier_mapper.to_domain(orm)

    def delete(self, modifier_id: UUID) -> None:
        result = self._session.execute(
            text("SELECT 1 FROM order_item_modifier WHERE modifier_id = :mid LIMIT 1"),
            {"mid": str(modifier_id)},
        )
        if result.fetchone() is not None:
            raise ModifierHasHistoryError(
                f"Modifier {modifier_id} cannot be deleted because it is referenced in order history"
            )
        orm = self._session.get(ModifierORM, str(modifier_id))
        self._session.delete(orm)
        self._session.commit()
