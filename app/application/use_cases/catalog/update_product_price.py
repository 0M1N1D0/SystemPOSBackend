from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from app.domain.entities.product import Product
from app.domain.enums import AuditAction
from app.domain.exceptions import ProductNotFoundError
from app.domain.repositories.i_product_repository import IProductRepository
from app.domain.services.i_audit_log_service import IAuditLogService


@dataclass
class UpdateProductPriceInput:
    product_id: UUID
    new_price: Decimal


class UpdateProductPriceUseCase:
    def __init__(
        self,
        product_repo: IProductRepository,
        audit_service: IAuditLogService,
        actor_user_id: UUID,
    ) -> None:
        self._repo = product_repo
        self._audit = audit_service
        self._actor = actor_user_id

    def execute(self, input_data: UpdateProductPriceInput) -> Product:
        product = self._repo.find_by_id(input_data.product_id)
        if product is None:
            raise ProductNotFoundError(f"Product {input_data.product_id} not found")

        previous_price = product.base_price
        product.base_price = input_data.new_price

        updated = self._repo.update(product)
        self._audit.log(
            user_id=self._actor,
            action=AuditAction.PRODUCT_PRICE_UPDATED,
            details={
                "product_id": str(updated.id),
                "previous_price": str(previous_price),
                "new_price": str(updated.base_price),
            },
        )
        return updated
