from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from app.domain.entities.category import Category
from app.domain.enums import AuditAction
from app.domain.exceptions import CategoryNotFoundError
from app.domain.repositories.i_category_repository import ICategoryRepository
from app.domain.services.i_audit_log_service import IAuditLogService


@dataclass
class UpdateCategoryInput:
    category_id: UUID
    name: Optional[str] = None
    description: Optional[str] = None
    sort_order: Optional[int] = None


class UpdateCategoryUseCase:
    def __init__(
        self,
        category_repo: ICategoryRepository,
        audit_service: IAuditLogService,
        actor_user_id: UUID,
    ) -> None:
        self._repo = category_repo
        self._audit = audit_service
        self._actor = actor_user_id

    def execute(self, input_data: UpdateCategoryInput) -> Category:
        category = self._repo.find_by_id(input_data.category_id)
        if category is None:
            raise CategoryNotFoundError(f"Category {input_data.category_id} not found")

        if input_data.name is not None:
            category.name = input_data.name
        if input_data.description is not None:
            category.description = input_data.description
        if input_data.sort_order is not None:
            category.sort_order = input_data.sort_order

        updated = self._repo.update(category)
        self._audit.log(
            user_id=self._actor,
            action=AuditAction.CATEGORY_UPDATED,
            details={"category_id": str(updated.id), "name": updated.name},
        )
        return updated
