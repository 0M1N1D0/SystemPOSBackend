import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from app.domain.entities.user import User
from app.domain.enums import AuditAction
from app.domain.exceptions import (
    BranchNotFoundError,
    EmailAlreadyExistsError,
    RoleNotFoundError,
)
from app.domain.repositories.i_branch_repository import IBranchRepository
from app.domain.repositories.i_role_repository import IRoleRepository
from app.domain.repositories.i_user_repository import IUserRepository
from app.domain.services.i_audit_log_service import IAuditLogService
from app.domain.services.i_password_hasher import IPasswordHasher


@dataclass
class CreateUserInput:
    role_id: UUID
    given_name: str
    paternal_surname: str
    pin: str
    branch_id: Optional[UUID] = None
    maternal_surname: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None


class CreateUserUseCase:
    def __init__(
        self,
        user_repo: IUserRepository,
        role_repo: IRoleRepository,
        branch_repo: IBranchRepository,
        hasher: IPasswordHasher,
        audit_service: IAuditLogService,
        actor_user_id: UUID,
    ) -> None:
        self._user_repo = user_repo
        self._role_repo = role_repo
        self._branch_repo = branch_repo
        self._hasher = hasher
        self._audit_service = audit_service
        self._actor_user_id = actor_user_id

    def execute(self, input_data: CreateUserInput) -> User:
        role = self._role_repo.find_by_id(input_data.role_id)
        if role is None:
            raise RoleNotFoundError(f"Role {input_data.role_id} not found")

        if input_data.branch_id is not None:
            branch = self._branch_repo.find_by_id(input_data.branch_id)
            if branch is None:
                raise BranchNotFoundError(f"Branch {input_data.branch_id} not found")

        if input_data.email is not None:
            existing = self._user_repo.find_by_email(input_data.email)
            if existing is not None:
                raise EmailAlreadyExistsError(f"Email {input_data.email} already in use")

        user = User(
            id=uuid.uuid4(),
            role_id=input_data.role_id,
            role_name=role.name,
            given_name=input_data.given_name,
            paternal_surname=input_data.paternal_surname,
            maternal_surname=input_data.maternal_surname,
            branch_id=input_data.branch_id,
            email=input_data.email,
            pin_hash=self._hasher.hash(input_data.pin),
            password_hash=self._hasher.hash(input_data.password) if input_data.password else None,
            is_active=True,
            created_at=datetime.now(timezone.utc),
        )
        saved = self._user_repo.save(user)

        self._audit_service.log(
            user_id=self._actor_user_id,
            action=AuditAction.USER_CREATED,
            details={
                "user_id": str(saved.id),
                "given_name": saved.given_name,
                "role": saved.role_name.value,
            },
        )
        return saved
