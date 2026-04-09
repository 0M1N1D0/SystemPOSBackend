from uuid import UUID

from app.domain.entities.category import Category
from app.domain.exceptions import CategoryNotFoundError
from app.domain.repositories.i_category_repository import ICategoryRepository


class GetCategoryUseCase:
    def __init__(self, category_repo: ICategoryRepository) -> None:
        self._repo = category_repo

    def execute(self, category_id: UUID) -> Category:
        category = self._repo.find_by_id(category_id)
        if category is None:
            raise CategoryNotFoundError(f"Category {category_id} not found")
        return category
