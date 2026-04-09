from app.domain.entities.category import Category
from app.domain.repositories.i_category_repository import ICategoryRepository


class ListCategoriesUseCase:
    def __init__(self, category_repo: ICategoryRepository) -> None:
        self._repo = category_repo

    def execute(self) -> list[Category]:
        return self._repo.find_all()
