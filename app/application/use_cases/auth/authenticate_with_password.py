from dataclasses import dataclass

from app.domain.enums import AuditAction
from app.domain.exceptions import InvalidCredentialsError, UserInactiveError
from app.domain.repositories.i_user_repository import IUserRepository
from app.domain.services.i_audit_log_service import IAuditLogService
from app.domain.services.i_password_hasher import IPasswordHasher
from app.domain.services.i_token_service import ITokenService
from app.application.use_cases.auth.authenticate_with_pin import TokenOutput


@dataclass
class AuthenticateWithPasswordInput:
    email: str
    password: str


class AuthenticateWithPasswordUseCase:
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

    def execute(self, input_data: AuthenticateWithPasswordInput) -> TokenOutput:
        user = self._user_repo.find_by_email(input_data.email)

        # Intentionally vague error to prevent email enumeration
        if user is None or user.password_hash is None:
            raise InvalidCredentialsError("Invalid credentials")

        if not user.is_active:
            self._audit_service.log(
                user_id=user.id,
                action=AuditAction.USER_LOGIN_FAILED,
                details={"method": "password", "reason": "user_inactive"},
            )
            raise UserInactiveError("User account is deactivated")

        if not self._hasher.verify(input_data.password, user.password_hash):
            self._audit_service.log(
                user_id=user.id,
                action=AuditAction.USER_LOGIN_FAILED,
                details={"method": "password", "reason": "invalid_password"},
            )
            raise InvalidCredentialsError("Invalid credentials")

        token = self._token_service.create_access_token(
            user_id=user.id, role=user.role_name, pin_based=False
        )
        self._audit_service.log(
            user_id=user.id,
            action=AuditAction.USER_LOGIN,
            details={"method": "password"},
        )
        return TokenOutput(access_token=token)
