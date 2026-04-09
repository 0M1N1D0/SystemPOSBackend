from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from app.domain.entities.product import Product
from app.domain.enums import AuditAction
from app.domain.exceptions import CategoryNotFoundError, ProductNotFoundError, TaxRateNotFoundError
from app.domain.repositories.i_category_repository import ICategoryRepository
from app.domain.repositories.i_product_repository import IProductRepository
from app.domain.repositories.i_tax_rate_repository import ITaxRateRepository
from app.domain.services.i_audit_log_service import IAuditLogService


@dataclass
class UpdateProductInput:
    product_id: UUID
    name: Optional[str] = None
    is_available: Optional[bool] = None
    sort_order: Optional[int] = None
    category_id: Optional[UUID] = None
    tax_rate_id: Optional[UUID] = None


class UpdateProductUseCase:
    def __init__(
        self,
        product_repo: IProductRepository,
        category_repo: ICategoryRepository,
        tax_rate_repo: ITaxRateRepository,
        audit_service: IAuditLogService,
        actor_user_id: UUID,
    ) -> None:
        self._product_repo = product_repo
        self._category_repo = category_repo
        self._tax_rate_repo = tax_rate_repo
        self._audit = audit_service
        self._actor = actor_user_id

    def execute(self, input_data: UpdateProductInput) -> Product:
        product = self._product_repo.find_by_id(input_data.product_id)
        if product is None:
            raise ProductNotFoundError(f"Product {input_data.product_id} not found")

        if input_data.category_id is not None:
            if self._category_repo.find_by_id(input_data.category_id) is None:
                raise CategoryNotFoundError(f"Category {input_data.category_id} not found")
            product.category_id = input_data.category_id

        if input_data.tax_rate_id is not None:
            if self._tax_rate_repo.find_by_id(input_data.tax_rate_id) is None:
                raise TaxRateNotFoundError(f"TaxRate {input_data.tax_rate_id} not found")
            product.tax_rate_id = input_data.tax_rate_id

        if input_data.name is not None:
            product.name = input_data.name
        if input_data.is_available is not None:
            product.is_available = input_data.is_available
        if input_data.sort_order is not None:
            product.sort_order = input_data.sort_order

        updated = self._product_repo.update(product)
        self._audit.log(
            user_id=self._actor,
            action=AuditAction.PRODUCT_UPDATED,
            details={"product_id": str(updated.id), "name": updated.name},
        )
        return updated
