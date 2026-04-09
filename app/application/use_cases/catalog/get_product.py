from uuid import UUID

from app.domain.entities.product import Product
from app.domain.exceptions import ProductNotFoundError
from app.domain.repositories.i_product_repository import IProductRepository


class GetProductUseCase:
    def __init__(self, product_repo: IProductRepository) -> None:
        self._repo = product_repo

    def execute(self, product_id: UUID) -> Product:
        product = self._repo.find_by_id(product_id)
        if product is None:
            raise ProductNotFoundError(f"Product {product_id} not found")
        return product
