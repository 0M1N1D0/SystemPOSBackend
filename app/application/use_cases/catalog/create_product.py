import uuid
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional
from uuid import UUID

from app.domain.entities.product import Product
from app.domain.enums import AuditAction
from app.domain.exceptions import CategoryNotFoundError, TaxRateNotFoundError
from app.domain.repositories.i_category_repository import ICategoryRepository
from app.domain.repositories.i_product_repository import IProductRepository
from app.domain.repositories.i_tax_rate_repository import ITaxRateRepository
from app.domain.services.i_audit_log_service import IAuditLogService


@dataclass
class CreateProductInput:
    category_id: UUID
    name: str
    base_price: Decimal
    is_available: bool = True
    sort_order: Optional[int] = None
    tax_rate_id: Optional[UUID] = None


class CreateProductUseCase:
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

    def execute(self, input_data: CreateProductInput) -> Product:
        if self._category_repo.find_by_id(input_data.category_id) is None:
            raise CategoryNotFoundError(f"Category {input_data.category_id} not found")

        if input_data.tax_rate_id is not None:
            if self._tax_rate_repo.find_by_id(input_data.tax_rate_id) is None:
                raise TaxRateNotFoundError(f"TaxRate {input_data.tax_rate_id} not found")

        product = Product(
            id=uuid.uuid4(),
            category_id=input_data.category_id,
            name=input_data.name,
            base_price=input_data.base_price,
            is_available=input_data.is_available,
            sort_order=input_data.sort_order,
            tax_rate_id=input_data.tax_rate_id,
        )
        saved = self._product_repo.save(product)
        self._audit.log(
            user_id=self._actor,
            action=AuditAction.PRODUCT_CREATED,
            details={
                "product_id": str(saved.id),
                "name": saved.name,
                "base_price": str(saved.base_price),
                "category_id": str(saved.category_id),
            },
        )
        return saved
