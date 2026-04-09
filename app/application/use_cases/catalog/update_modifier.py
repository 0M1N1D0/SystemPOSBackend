from dataclasses import dataclass
from decimal import Decimal
from typing import Optional
from uuid import UUID

from app.domain.entities.modifier import Modifier
from app.domain.enums import AuditAction
from app.domain.exceptions import ModifierNotFoundError
from app.domain.repositories.i_modifier_repository import IModifierRepository
from app.domain.services.i_audit_log_service import IAuditLogService


@dataclass
class UpdateModifierInput:
    modifier_id: UUID
    name: Optional[str] = None
    extra_price: Optional[Decimal] = None


class UpdateModifierUseCase:
    def __init__(
        self,
        modifier_repo: IModifierRepository,
        audit_service: IAuditLogService,
        actor_user_id: UUID,
    ) -> None:
        self._repo = modifier_repo
        self._audit = audit_service
        self._actor = actor_user_id

    def execute(self, input_data: UpdateModifierInput) -> Modifier:
        modifier = self._repo.find_by_id(input_data.modifier_id)
        if modifier is None:
            raise ModifierNotFoundError(f"Modifier {input_data.modifier_id} not found")

        if input_data.name is not None:
            modifier.name = input_data.name
        if input_data.extra_price is not None:
            modifier.extra_price = input_data.extra_price

        updated = self._repo.update(modifier)
        self._audit.log(
            user_id=self._actor,
            action=AuditAction.MODIFIER_UPDATED,
            details={"modifier_id": str(updated.id), "name": updated.name},
        )
        return updated
