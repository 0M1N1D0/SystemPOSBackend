from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.entities.tax_rate import TaxRate
from app.domain.repositories.i_tax_rate_repository import ITaxRateRepository
from app.infrastructure.mappers import tax_rate_mapper
from app.infrastructure.orm.tax_rate import TaxRateORM


class SqlTaxRateRepository(ITaxRateRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, tax_rate: TaxRate) -> TaxRate:
        orm = tax_rate_mapper.to_orm(tax_rate)
        self._session.add(orm)
        self._session.commit()
        self._session.refresh(orm)
        return tax_rate_mapper.to_domain(orm)

    def find_by_id(self, tax_rate_id: UUID) -> Optional[TaxRate]:
        orm = self._session.get(TaxRateORM, str(tax_rate_id))
        return tax_rate_mapper.to_domain(orm) if orm else None

    def find_default(self) -> Optional[TaxRate]:
        orm = (
            self._session.query(TaxRateORM)
            .filter(TaxRateORM.is_default.is_(True))
            .first()
        )
        return tax_rate_mapper.to_domain(orm) if orm else None

    def find_all(self) -> list[TaxRate]:
        rows = self._session.query(TaxRateORM).order_by(TaxRateORM.name).all()
        return [tax_rate_mapper.to_domain(r) for r in rows]

    def update(self, tax_rate: TaxRate) -> TaxRate:
        orm = self._session.get(TaxRateORM, str(tax_rate.id))
        orm.name = tax_rate.name
        orm.rate = tax_rate.rate
        orm.is_default = tax_rate.is_default
        orm.is_active = tax_rate.is_active
        self._session.commit()
        self._session.refresh(orm)
        return tax_rate_mapper.to_domain(orm)

    def clear_default(self) -> None:
        self._session.query(TaxRateORM).filter(
            TaxRateORM.is_default.is_(True)
        ).update({"is_default": False})
        self._session.commit()
