from uuid import UUID

from app.domain.enums import AuditAction
from app.domain.exceptions import ModifierNotFoundError
from app.domain.repositories.i_modifier_repository import IModifierRepository
from app.domain.services.i_audit_log_service import IAuditLogService


class DeleteModifierUseCase:
    """
    Deletes a modifier. Raises ModifierHasHistoryError (via repository) if the
    modifier is referenced in any order_item_modifier row (RESTRICT rule).
    """

    def __init__(
        self,
        modifier_repo: IModifierRepository,
        audit_service: IAuditLogService,
        actor_user_id: UUID,
    ) -> None:
        self._repo = modifier_repo
        self._audit = audit_service
        self._actor = actor_user_id

    def execute(self, modifier_id: UUID) -> None:
        modifier = self._repo.find_by_id(modifier_id)
        if modifier is None:
            raise ModifierNotFoundError(f"Modifier {modifier_id} not found")

        # Repository raises ModifierHasHistoryError if there is order history
        self._repo.delete(modifier_id)

        self._audit.log(
            user_id=self._actor,
            action=AuditAction.MODIFIER_DELETED,
            details={"modifier_id": str(modifier_id), "name": modifier.name},
        )
