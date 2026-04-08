import uuid

from app.domain.entities.tax_rate import TaxRate
from app.infrastructure.orm.tax_rate import TaxRateORM


def to_domain(orm: TaxRateORM) -> TaxRate:
    return TaxRate(
        id=uuid.UUID(orm.id),
        name=orm.name,
        rate=orm.rate,
        is_default=orm.is_default,
        is_active=orm.is_active,
    )


def to_orm(entity: TaxRate) -> TaxRateORM:
    return TaxRateORM(
        id=str(entity.id),
        name=entity.name,
        rate=entity.rate,
        is_default=entity.is_default,
        is_active=entity.is_active,
    )
