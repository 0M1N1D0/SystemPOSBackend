import uuid
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from app.domain.entities.tax_rate import TaxRate
from app.domain.enums import AuditAction
from app.domain.repositories.i_tax_rate_repository import ITaxRateRepository
from app.domain.services.i_audit_log_service import IAuditLogService


@dataclass
class CreateTaxRateInput:
    name: str
    rate: Decimal
    is_default: bool = False


class CreateTaxRateUseCase:
    def __init__(
        self,
        tax_rate_repo: ITaxRateRepository,
        audit_service: IAuditLogService,
        actor_user_id: UUID,
    ) -> None:
        self._repo = tax_rate_repo
        self._audit = audit_service
        self._actor = actor_user_id

    def execute(self, input_data: CreateTaxRateInput) -> TaxRate:
        if input_data.is_default:
            self._repo.clear_default()

        tax_rate = TaxRate(
            id=uuid.uuid4(),
            name=input_data.name,
            rate=input_data.rate,
            is_default=input_data.is_default,
            is_active=True,
        )
        saved = self._repo.save(tax_rate)

        self._audit.log(
            user_id=self._actor,
            action=AuditAction.TAX_RATE_CREATED,
            details={"tax_rate_id": str(saved.id), "name": saved.name, "rate": str(saved.rate)},
        )
        return saved
