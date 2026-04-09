from uuid import UUID

from app.domain.entities.product import Product
from app.domain.exceptions import CategoryNotFoundError
from app.domain.repositories.i_category_repository import ICategoryRepository
from app.domain.repositories.i_product_repository import IProductRepository


class ListProductsByCategoryUseCase:
    def __init__(
        self,
        product_repo: IProductRepository,
        category_repo: ICategoryRepository,
    ) -> None:
        self._product_repo = product_repo
        self._category_repo = category_repo

    def execute(self, category_id: UUID) -> list[Product]:
        if self._category_repo.find_by_id(category_id) is None:
            raise CategoryNotFoundError(f"Category {category_id} not found")
        return self._product_repo.find_by_category(category_id)
