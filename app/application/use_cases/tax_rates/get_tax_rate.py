from uuid import UUID

from app.domain.entities.tax_rate import TaxRate
from app.domain.exceptions import TaxRateNotFoundError
from app.domain.repositories.i_tax_rate_repository import ITaxRateRepository


class GetTaxRateUseCase:
    def __init__(self, tax_rate_repo: ITaxRateRepository) -> None:
        self._repo = tax_rate_repo

    def execute(self, tax_rate_id: UUID) -> TaxRate:
        tax_rate = self._repo.find_by_id(tax_rate_id)
        if tax_rate is None:
            raise TaxRateNotFoundError(f"TaxRate {tax_rate_id} not found")
        return tax_rate
