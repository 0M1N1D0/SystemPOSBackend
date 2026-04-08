from app.domain.entities.tax_rate import TaxRate
from app.domain.repositories.i_tax_rate_repository import ITaxRateRepository


class ListTaxRatesUseCase:
    def __init__(self, tax_rate_repo: ITaxRateRepository) -> None:
        self._repo = tax_rate_repo

    def execute(self) -> list[TaxRate]:
        return self._repo.find_all()
