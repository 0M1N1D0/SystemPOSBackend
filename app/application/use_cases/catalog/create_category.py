import uuid
from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from app.domain.entities.category import Category
from app.domain.enums import AuditAction
from app.domain.repositories.i_category_repository import ICategoryRepository
from app.domain.services.i_audit_log_service import IAuditLogService


@dataclass
class CreateCategoryInput:
    name: str
    description: Optional[str] = None
    sort_order: Optional[int] = None


class CreateCategoryUseCase:
    def __init__(
        self,
        category_repo: ICategoryRepository,
        audit_service: IAuditLogService,
        actor_user_id: UUID,
    ) -> None:
        self._repo = category_repo
        self._audit = audit_service
        self._actor = actor_user_id

    def execute(self, input_data: CreateCategoryInput) -> Category:
        category = Category(
            id=uuid.uuid4(),
            name=input_data.name,
            description=input_data.description,
            sort_order=input_data.sort_order,
        )
        saved = self._repo.save(category)
        self._audit.log(
            user_id=self._actor,
            action=AuditAction.CATEGORY_CREATED,
            details={"category_id": str(saved.id), "name": saved.name},
        )
        return saved
