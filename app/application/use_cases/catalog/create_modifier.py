import uuid
from dataclasses import dataclass, field
from decimal import Decimal
from uuid import UUID

from app.domain.entities.modifier import Modifier
from app.domain.enums import AuditAction
from app.domain.exceptions import ProductNotFoundError
from app.domain.repositories.i_modifier_repository import IModifierRepository
from app.domain.repositories.i_product_repository import IProductRepository
from app.domain.services.i_audit_log_service import IAuditLogService


@dataclass
class CreateModifierInput:
    product_id: UUID
    name: str
    extra_price: Decimal = field(default=Decimal("0.0"))


class CreateModifierUseCase:
    def __init__(
        self,
        modifier_repo: IModifierRepository,
        product_repo: IProductRepository,
        audit_service: IAuditLogService,
        actor_user_id: UUID,
    ) -> None:
        self._modifier_repo = modifier_repo
        self._product_repo = product_repo
        self._audit = audit_service
        self._actor = actor_user_id

    def execute(self, input_data: CreateModifierInput) -> Modifier:
        if self._product_repo.find_by_id(input_data.product_id) is None:
            raise ProductNotFoundError(f"Product {input_data.product_id} not found")

        modifier = Modifier(
            id=uuid.uuid4(),
            product_id=input_data.product_id,
            name=input_data.name,
            extra_price=input_data.extra_price,
        )
        saved = self._modifier_repo.save(modifier)
        self._audit.log(
            user_id=self._actor,
            action=AuditAction.MODIFIER_CREATED,
            details={
                "modifier_id": str(saved.id),
                "product_id": str(saved.product_id),
                "name": saved.name,
                "extra_price": str(saved.extra_price),
            },
        )
        return saved
