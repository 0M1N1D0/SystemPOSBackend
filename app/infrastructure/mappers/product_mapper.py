import uuid

from app.domain.entities.product import Product
from app.infrastructure.orm.product import ProductORM


def to_domain(orm: ProductORM) -> Product:
    return Product(
        id=uuid.UUID(orm.id),
        category_id=uuid.UUID(orm.category_id),
        name=orm.name,
        base_price=orm.base_price,
        is_available=orm.is_available,
        sort_order=orm.sort_order,
        tax_rate_id=uuid.UUID(orm.tax_rate_id) if orm.tax_rate_id else None,
    )


def to_orm(entity: Product) -> ProductORM:
    return ProductORM(
        id=str(entity.id),
        category_id=str(entity.category_id),
        tax_rate_id=str(entity.tax_rate_id) if entity.tax_rate_id else None,
        name=entity.name,
        base_price=entity.base_price,
        is_available=entity.is_available,
        sort_order=entity.sort_order,
    )
