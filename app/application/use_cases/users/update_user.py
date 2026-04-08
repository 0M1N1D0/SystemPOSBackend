from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from app.domain.entities.user import User
from app.domain.enums import AuditAction
from app.domain.exceptions import BranchNotFoundError, UserNotFoundError
from app.domain.repositories.i_branch_repository import IBranchRepository
from app.domain.repositories.i_user_repository import IUserRepository
from app.domain.services.i_audit_log_service import IAuditLogService


@dataclass
class UpdateUserInput:
    user_id: UUID
    given_name: Optional[str] = None
    paternal_surname: Optional[str] = None
    maternal_surname: Optional[str] = None
    branch_id: Optional[UUID] = None


class UpdateUserUseCase:
    def __init__(
        self,
        user_repo: IUserRepository,
        branch_repo: IBranchRepository,
        audit_service: IAuditLogService,
        actor_user_id: UUID,
    ) -> None:
        self._user_repo = user_repo
        self._branch_repo = branch_repo
        self._audit_service = audit_service
        self._actor_user_id = actor_user_id

    def execute(self, input_data: UpdateUserInput) -> User:
        user = self._user_repo.find_by_id(input_data.user_id)
        if user is None:
            raise UserNotFoundError(f"User {input_data.user_id} not found")

        if input_data.branch_id is not None:
            branch = self._branch_repo.find_by_id(input_data.branch_id)
            if branch is None:
                raise BranchNotFoundError(f"Branch {input_data.branch_id} not found")

        changed_fields = []
        if input_data.given_name is not None:
            user.given_name = input_data.given_name
            changed_fields.append("given_name")
        if input_data.paternal_surname is not None:
            user.paternal_surname = input_data.paternal_surname
            changed_fields.append("paternal_surname")
        if input_data.maternal_surname is not None:
            user.maternal_surname = input_data.maternal_surname
            changed_fields.append("maternal_surname")
        if input_data.branch_id is not None:
            user.branch_id = input_data.branch_id
            changed_fields.append("branch_id")

        updated = self._user_repo.update(user)
        self._audit_service.log(
            user_id=self._actor_user_id,
            action=AuditAction.USER_UPDATED,
            details={"user_id": str(updated.id), "changed_fields": changed_fields},
        )
        return updated
