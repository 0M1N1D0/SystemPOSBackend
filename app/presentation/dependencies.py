from collections.abc import Generator
from uuid import UUID

from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.application.use_cases.auth.authenticate_with_password import (
    AuthenticateWithPasswordUseCase,
)
from app.application.use_cases.auth.authenticate_with_pin import (
    AuthenticateWithPinUseCase,
)
from app.application.use_cases.auth.logout import LogoutUseCase
from app.application.use_cases.branches.create_branch import CreateBranchUseCase
from app.application.use_cases.branches.deactivate_branch import DeactivateBranchUseCase
from app.application.use_cases.branches.get_branch import GetBranchUseCase
from app.application.use_cases.branches.list_branches import ListBranchesUseCase
from app.application.use_cases.branches.update_branch import UpdateBranchUseCase
from app.application.use_cases.users.change_password import ChangePasswordUseCase
from app.application.use_cases.users.change_pin import ChangePinUseCase
from app.application.use_cases.users.create_user import CreateUserUseCase
from app.application.use_cases.users.deactivate_user import DeactivateUserUseCase
from app.application.use_cases.users.get_user import GetUserUseCase
from app.application.use_cases.users.list_users import ListUsersUseCase
from app.application.use_cases.users.update_user import UpdateUserUseCase
from app.application.use_cases.tax_rates.create_tax_rate import CreateTaxRateUseCase
from app.application.use_cases.tax_rates.update_tax_rate import UpdateTaxRateUseCase
from app.application.use_cases.tax_rates.deactivate_tax_rate import DeactivateTaxRateUseCase
from app.application.use_cases.tax_rates.set_default_tax_rate import SetDefaultTaxRateUseCase
from app.application.use_cases.tax_rates.list_tax_rates import ListTaxRatesUseCase
from app.application.use_cases.tax_rates.get_tax_rate import GetTaxRateUseCase
from app.config import settings
from app.domain.enums import RoleName
from app.domain.services.i_token_service import TokenPayload
from app.infrastructure.database import get_session
from app.infrastructure.repositories.audit_log_repository import SqlAuditLogRepository
from app.infrastructure.repositories.branch_repository import SqlBranchRepository
from app.infrastructure.repositories.role_repository import SqlRoleRepository
from app.infrastructure.repositories.user_repository import SqlUserRepository
from app.infrastructure.repositories.tax_rate_repository import SqlTaxRateRepository
from app.infrastructure.services.audit_log_service import AuditLogService
from app.infrastructure.services.bcrypt_hasher import BcryptHasher
from app.infrastructure.services.jwt_token_service import JwtTokenService

_security = HTTPBearer()
_hasher = BcryptHasher()


def get_token_service() -> JwtTokenService:
    return JwtTokenService(
        secret_key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
        pin_expire_minutes=settings.JWT_PIN_TOKEN_EXPIRE_MINUTES,
        password_expire_minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
    )


def get_current_token_payload(
    credentials: HTTPAuthorizationCredentials = Security(_security),
    token_service: JwtTokenService = Depends(get_token_service),
) -> TokenPayload:
    return token_service.decode_token(credentials.credentials)


def require_admin(
    payload: TokenPayload = Depends(get_current_token_payload),
) -> TokenPayload:
    if payload.role != RoleName.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    return payload


def require_manager_or_above(
    payload: TokenPayload = Depends(get_current_token_payload),
) -> TokenPayload:
    if payload.role not in (RoleName.ADMIN, RoleName.MANAGER):
        raise HTTPException(status_code=403, detail="Manager or Admin access required")
    return payload


# --- Infrastructure factories ---

def _audit_service(session: Session) -> AuditLogService:
    return AuditLogService(SqlAuditLogRepository(session))


# --- Auth use cases ---

def get_pin_auth_use_case(
    session: Session = Depends(get_session),
    token_service: JwtTokenService = Depends(get_token_service),
) -> AuthenticateWithPinUseCase:
    return AuthenticateWithPinUseCase(
        user_repo=SqlUserRepository(session),
        hasher=_hasher,
        token_service=token_service,
        audit_service=_audit_service(session),
    )


def get_password_auth_use_case(
    session: Session = Depends(get_session),
    token_service: JwtTokenService = Depends(get_token_service),
) -> AuthenticateWithPasswordUseCase:
    return AuthenticateWithPasswordUseCase(
        user_repo=SqlUserRepository(session),
        hasher=_hasher,
        token_service=token_service,
        audit_service=_audit_service(session),
    )


def get_logout_use_case(
    session: Session = Depends(get_session),
) -> LogoutUseCase:
    return LogoutUseCase(audit_service=_audit_service(session))


# --- Branch use cases ---

def get_create_branch_use_case(
    session: Session = Depends(get_session),
) -> CreateBranchUseCase:
    return CreateBranchUseCase(SqlBranchRepository(session))


def get_update_branch_use_case(
    session: Session = Depends(get_session),
) -> UpdateBranchUseCase:
    return UpdateBranchUseCase(SqlBranchRepository(session))


def get_deactivate_branch_use_case(
    session: Session = Depends(get_session),
) -> DeactivateBranchUseCase:
    return DeactivateBranchUseCase(SqlBranchRepository(session))


def get_branch_use_case(
    session: Session = Depends(get_session),
) -> GetBranchUseCase:
    return GetBranchUseCase(SqlBranchRepository(session))


def get_list_branches_use_case(
    session: Session = Depends(get_session),
) -> ListBranchesUseCase:
    return ListBranchesUseCase(SqlBranchRepository(session))


# --- User use cases ---

def get_create_user_use_case(
    session: Session = Depends(get_session),
    payload: TokenPayload = Depends(get_current_token_payload),
) -> CreateUserUseCase:
    return CreateUserUseCase(
        user_repo=SqlUserRepository(session),
        role_repo=SqlRoleRepository(session),
        branch_repo=SqlBranchRepository(session),
        hasher=_hasher,
        audit_service=_audit_service(session),
        actor_user_id=payload.user_id,
    )


def get_update_user_use_case(
    session: Session = Depends(get_session),
    payload: TokenPayload = Depends(get_current_token_payload),
) -> UpdateUserUseCase:
    return UpdateUserUseCase(
        user_repo=SqlUserRepository(session),
        branch_repo=SqlBranchRepository(session),
        audit_service=_audit_service(session),
        actor_user_id=payload.user_id,
    )


def get_deactivate_user_use_case(
    session: Session = Depends(get_session),
    payload: TokenPayload = Depends(get_current_token_payload),
) -> DeactivateUserUseCase:
    return DeactivateUserUseCase(
        user_repo=SqlUserRepository(session),
        audit_service=_audit_service(session),
        actor_user_id=payload.user_id,
    )


def get_change_pin_use_case(
    session: Session = Depends(get_session),
) -> ChangePinUseCase:
    return ChangePinUseCase(
        user_repo=SqlUserRepository(session),
        hasher=_hasher,
        audit_service=_audit_service(session),
    )


def get_change_password_use_case(
    session: Session = Depends(get_session),
) -> ChangePasswordUseCase:
    return ChangePasswordUseCase(
        user_repo=SqlUserRepository(session),
        hasher=_hasher,
        audit_service=_audit_service(session),
    )


def get_get_user_use_case(
    session: Session = Depends(get_session),
) -> GetUserUseCase:
    return GetUserUseCase(SqlUserRepository(session))


def get_list_users_use_case(
    session: Session = Depends(get_session),
) -> ListUsersUseCase:
    return ListUsersUseCase(SqlUserRepository(session))


# --- Tax Rate use cases ---

def get_create_tax_rate_use_case(
    session: Session = Depends(get_session),
    payload: TokenPayload = Depends(get_current_token_payload),
) -> CreateTaxRateUseCase:
    return CreateTaxRateUseCase(
        tax_rate_repo=SqlTaxRateRepository(session),
        audit_service=_audit_service(session),
        actor_user_id=payload.user_id,
    )


def get_update_tax_rate_use_case(
    session: Session = Depends(get_session),
    payload: TokenPayload = Depends(get_current_token_payload),
) -> UpdateTaxRateUseCase:
    return UpdateTaxRateUseCase(
        tax_rate_repo=SqlTaxRateRepository(session),
        audit_service=_audit_service(session),
        actor_user_id=payload.user_id,
    )


def get_deactivate_tax_rate_use_case(
    session: Session = Depends(get_session),
    payload: TokenPayload = Depends(get_current_token_payload),
) -> DeactivateTaxRateUseCase:
    return DeactivateTaxRateUseCase(
        tax_rate_repo=SqlTaxRateRepository(session),
        audit_service=_audit_service(session),
        actor_user_id=payload.user_id,
    )


def get_set_default_tax_rate_use_case(
    session: Session = Depends(get_session),
    payload: TokenPayload = Depends(get_current_token_payload),
) -> SetDefaultTaxRateUseCase:
    return SetDefaultTaxRateUseCase(
        tax_rate_repo=SqlTaxRateRepository(session),
        audit_service=_audit_service(session),
        actor_user_id=payload.user_id,
    )


def get_list_tax_rates_use_case(
    session: Session = Depends(get_session),
) -> ListTaxRatesUseCase:
    return ListTaxRatesUseCase(SqlTaxRateRepository(session))


def get_get_tax_rate_use_case(
    session: Session = Depends(get_session),
) -> GetTaxRateUseCase:
    return GetTaxRateUseCase(SqlTaxRateRepository(session))
