from uuid import UUID

from app.domain.entities.product import Product
from app.domain.enums import AuditAction
from app.domain.exceptions import ProductNotFoundError
from app.domain.repositories.i_product_repository import IProductRepository
from app.domain.services.i_audit_log_service import IAuditLogService


class ToggleProductAvailabilityUseCase:
    def __init__(
        self,
        product_repo: IProductRepository,
        audit_service: IAuditLogService,
        actor_user_id: UUID,
    ) -> None:
        self._repo = product_repo
        self._audit = audit_service
        self._actor = actor_user_id

    def execute(self, product_id: UUID) -> Product:
        product = self._repo.find_by_id(product_id)
        if product is None:
            raise ProductNotFoundError(f"Product {product_id} not found")

        product.is_available = not product.is_available
        updated = self._repo.update(product)
        self._audit.log(
            user_id=self._actor,
            action=AuditAction.PRODUCT_TOGGLED,
            details={"product_id": str(updated.id), "is_available": updated.is_available},
        )
        return updated
