from uuid import UUID

from app.domain.entities.tax_rate import TaxRate
from app.domain.enums import AuditAction
from app.domain.exceptions import TaxRateNotFoundError, BusinessRuleViolationError
from app.domain.repositories.i_tax_rate_repository import ITaxRateRepository
from app.domain.services.i_audit_log_service import IAuditLogService


class SetDefaultTaxRateUseCase:
    def __init__(
        self,
        tax_rate_repo: ITaxRateRepository,
        audit_service: IAuditLogService,
        actor_user_id: UUID,
    ) -> None:
        self._repo = tax_rate_repo
        self._audit = audit_service
        self._actor = actor_user_id

    def execute(self, tax_rate_id: UUID) -> TaxRate:
        tax_rate = self._repo.find_by_id(tax_rate_id)
        if tax_rate is None:
            raise TaxRateNotFoundError(f"TaxRate {tax_rate_id} not found")

        if not tax_rate.is_active:
            raise BusinessRuleViolationError("Cannot set an inactive tax rate as default.")

        if tax_rate.is_default:
            return tax_rate  # already the default, nothing to do

        # Atomic swap: clear existing default, then set the new one
        self._repo.clear_default()
        tax_rate.is_default = True
        updated = self._repo.update(tax_rate)

        self._audit.log(
            user_id=self._actor,
            action=AuditAction.TAX_RATE_DEFAULT_CHANGED,
            details={"new_default_tax_rate_id": str(updated.id)},
        )
        return updated
