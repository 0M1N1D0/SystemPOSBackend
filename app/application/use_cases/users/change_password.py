from dataclasses import dataclass
from uuid import UUID

from app.domain.entities.user import User
from app.domain.enums import AuditAction
from app.domain.exceptions import BusinessRuleViolationError, InvalidCredentialsError, UserNotFoundError
from app.domain.repositories.i_user_repository import IUserRepository
from app.domain.services.i_audit_log_service import IAuditLogService
from app.domain.services.i_password_hasher import IPasswordHasher


@dataclass
class ChangePasswordInput:
    user_id: UUID
    current_password: str
    new_password: str


class ChangePasswordUseCase:
    def __init__(
        self,
        user_repo: IUserRepository,
        hasher: IPasswordHasher,
        audit_service: IAuditLogService,
    ) -> None:
        self._user_repo = user_repo
        self._hasher = hasher
        self._audit_service = audit_service

    def execute(self, input_data: ChangePasswordInput) -> User:
        user = self._user_repo.find_by_id(input_data.user_id)
        if user is None:
            raise UserNotFoundError(f"User {input_data.user_id} not found")

        if user.password_hash is None:
            raise BusinessRuleViolationError("User does not have a password set")

        if not self._hasher.verify(input_data.current_password, user.password_hash):
            raise InvalidCredentialsError("Current password is incorrect")

        user.password_hash = self._hasher.hash(input_data.new_password)
        updated = self._user_repo.update(user)

        self._audit_service.log(
            user_id=input_data.user_id,
            action=AuditAction.USER_PASSWORD_CHANGED,
            details={"user_id": str(input_data.user_id)},
        )
        return updated
