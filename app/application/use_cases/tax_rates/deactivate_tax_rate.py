from uuid import UUID

from app.domain.enums import AuditAction
from app.domain.exceptions import TaxRateIsDefaultError, TaxRateNotFoundError
from app.domain.repositories.i_tax_rate_repository import ITaxRateRepository
from app.domain.services.i_audit_log_service import IAuditLogService


class DeactivateTaxRateUseCase:
    def __init__(
        self,
        tax_rate_repo: ITaxRateRepository,
        audit_service: IAuditLogService,
        actor_user_id: UUID,
    ) -> None:
        self._repo = tax_rate_repo
        self._audit = audit_service
        self._actor = actor_user_id

    def execute(self, tax_rate_id: UUID) -> None:
        tax_rate = self._repo.find_by_id(tax_rate_id)
        if tax_rate is None:
            raise TaxRateNotFoundError(f"TaxRate {tax_rate_id} not found")

        if tax_rate.is_default:
            raise TaxRateIsDefaultError(
                "Cannot deactivate the default tax rate. Assign another rate as default first."
            )

        tax_rate.is_active = False
        self._repo.update(tax_rate)

        self._audit.log(
            user_id=self._actor,
            action=AuditAction.TAX_RATE_DEACTIVATED,
            details={"tax_rate_id": str(tax_rate_id)},
        )
