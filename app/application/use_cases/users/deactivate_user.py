from uuid import UUID

from app.domain.entities.user import User
from app.domain.enums import AuditAction
from app.domain.exceptions import UserNotFoundError
from app.domain.repositories.i_user_repository import IUserRepository
from app.domain.services.i_audit_log_service import IAuditLogService


class DeactivateUserUseCase:
    def __init__(
        self,
        user_repo: IUserRepository,
        audit_service: IAuditLogService,
        actor_user_id: UUID,
    ) -> None:
        self._user_repo = user_repo
        self._audit_service = audit_service
        self._actor_user_id = actor_user_id

    def execute(self, user_id: UUID) -> User:
        user = self._user_repo.find_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"User {user_id} not found")

        user.is_active = False
        updated = self._user_repo.update(user)

        self._audit_service.log(
            user_id=self._actor_user_id,
            action=AuditAction.USER_DEACTIVATED,
            details={"user_id": str(user_id), "given_name": user.given_name},
        )
        return updated
