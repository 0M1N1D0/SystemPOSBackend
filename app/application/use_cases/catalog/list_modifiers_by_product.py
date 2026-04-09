from uuid import UUID

from app.domain.entities.modifier import Modifier
from app.domain.exceptions import ProductNotFoundError
from app.domain.repositories.i_modifier_repository import IModifierRepository
from app.domain.repositories.i_product_repository import IProductRepository


class ListModifiersByProductUseCase:
    def __init__(
        self,
        modifier_repo: IModifierRepository,
        product_repo: IProductRepository,
    ) -> None:
        self._modifier_repo = modifier_repo
        self._product_repo = product_repo

    def execute(self, product_id: UUID) -> list[Modifier]:
        if self._product_repo.find_by_id(product_id) is None:
            raise ProductNotFoundError(f"Product {product_id} not found")
        return self._modifier_repo.find_by_product(product_id)
