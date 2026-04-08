from dataclasses import dataclass
from uuid import UUID

from app.domain.enums import AuditAction
from app.domain.exceptions import InvalidCredentialsError, UserInactiveError, UserNotFoundError
from app.domain.repositories.i_user_repository import IUserRepository
from app.domain.services.i_audit_log_service import IAuditLogService
from app.domain.services.i_password_hasher import IPasswordHasher
from app.domain.services.i_token_service import ITokenService


@dataclass
class AuthenticateWithPinInput:
    user_id: UUID
    pin: str


@dataclass
class TokenOutput:
    access_token: str
    token_type: str = "bearer"


class AuthenticateWithPinUseCase:
    def __init__(
        self,
        user_repo: IUserRepository,
        hasher: IPasswordHasher,
        token_service: ITokenService,
        audit_service: IAuditLogService,
    ) -> None:
        self._user_repo = user_repo
        self._hasher = hasher
        self._token_service = token_service
        self._audit_service = audit_service

    def execute(self, input_data: AuthenticateWithPinInput) -> TokenOutput:
        user = self._user_repo.find_by_id(input_data.user_id)
        if user is None:
            raise UserNotFoundError(f"User {input_data.user_id} not found")

        if not user.is_active:
            self._audit_service.log(
                user_id=input_data.user_id,
                action=AuditAction.USER_LOGIN_FAILED,
                details={"method": "pin", "reason": "user_inactive"},
            )
            raise UserInactiveError("User account is deactivated")

        if not self._hasher.verify(input_data.pin, user.pin_hash):
            self._audit_service.log(
                user_id=input_data.user_id,
                action=AuditAction.USER_LOGIN_FAILED,
                details={"method": "pin", "reason": "invalid_pin"},
            )
            raise InvalidCredentialsError("Invalid PIN")

        token = self._token_service.create_access_token(
            user_id=user.id, role=user.role_name, pin_based=True
        )
        self._audit_service.log(
            user_id=user.id,
            action=AuditAction.USER_LOGIN,
            details={"method": "pin"},
        )
        return TokenOutput(access_token=token)
