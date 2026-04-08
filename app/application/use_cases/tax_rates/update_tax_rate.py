from dataclasses import dataclass
from decimal import Decimal
from typing import Optional
from uuid import UUID

from app.domain.entities.tax_rate import TaxRate
from app.domain.enums import AuditAction
from app.domain.exceptions import TaxRateNotFoundError
from app.domain.repositories.i_tax_rate_repository import ITaxRateRepository
from app.domain.services.i_audit_log_service import IAuditLogService


@dataclass
class UpdateTaxRateInput:
    tax_rate_id: UUID
    name: Optional[str] = None
    rate: Optional[Decimal] = None


class UpdateTaxRateUseCase:
    def __init__(
        self,
        tax_rate_repo: ITaxRateRepository,
        audit_service: IAuditLogService,
        actor_user_id: UUID,
    ) -> None:
        self._repo = tax_rate_repo
        self._audit = audit_service
        self._actor = actor_user_id

    def execute(self, input_data: UpdateTaxRateInput) -> TaxRate:
        tax_rate = self._repo.find_by_id(input_data.tax_rate_id)
        if tax_rate is None:
            raise TaxRateNotFoundError(f"TaxRate {input_data.tax_rate_id} not found")

        if input_data.name is not None:
            tax_rate.name = input_data.name
        if input_data.rate is not None:
            tax_rate.rate = input_data.rate
            tax_rate.__post_init__()  # re-validate rate range

        updated = self._repo.update(tax_rate)
        self._audit.log(
            user_id=self._actor,
            action=AuditAction.TAX_RATE_UPDATED,
            details={"tax_rate_id": str(updated.id)},
        )
        return updated
