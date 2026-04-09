from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.entities.product import Product
from app.domain.repositories.i_product_repository import IProductRepository
from app.infrastructure.mappers import product_mapper
from app.infrastructure.orm.product import ProductORM


class SqlProductRepository(IProductRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, product: Product) -> Product:
        orm = product_mapper.to_orm(product)
        self._session.add(orm)
        self._session.commit()
        self._session.refresh(orm)
        return product_mapper.to_domain(orm)

    def find_by_id(self, product_id: UUID) -> Optional[Product]:
        orm = self._session.get(ProductORM, str(product_id))
        return product_mapper.to_domain(orm) if orm else None

    def find_by_category(self, category_id: UUID) -> list[Product]:
        rows = (
            self._session.query(ProductORM)
            .filter(ProductORM.category_id == str(category_id))
            .order_by(ProductORM.sort_order.nulls_last(), ProductORM.name)
            .all()
        )
        return [product_mapper.to_domain(r) for r in rows]

    def update(self, product: Product) -> Product:
        orm = self._session.get(ProductORM, str(product.id))
        orm.category_id = str(product.category_id)
        orm.tax_rate_id = str(product.tax_rate_id) if product.tax_rate_id else None
        orm.name = product.name
        orm.base_price = product.base_price
        orm.is_available = product.is_available
        orm.sort_order = product.sort_order
        self._session.commit()
        self._session.refresh(orm)
        return product_mapper.to_domain(orm)
