import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from uuid import UUID

from app.domain.entities.order import OrderItem, OrderItemModifier
from app.domain.enums import AuditAction, OrderItemStatus
from app.domain.exceptions import (
    DefaultTaxRateNotFoundError,
    ModifierNotFoundError,
    OrderAlreadyClosedError,
    OrderNotFoundError,
    ProductNotFoundError,
)
from app.domain.repositories.i_modifier_repository import IModifierRepository
from app.domain.repositories.i_order_repository import IOrderRepository
from app.domain.repositories.i_product_repository import IProductRepository
from app.domain.repositories.i_tax_rate_repository import ITaxRateRepository
from app.domain.services.i_audit_log_service import IAuditLogService


@dataclass
class AddOrderItemInput:
    order_id: UUID
    product_id: UUID
    quantity: int
    notes: Optional[str] = None
    modifier_ids: list[UUID] = field(default_factory=list)


class AddOrderItemUseCase:
    def __init__(
        self,
        order_repo: IOrderRepository,
        product_repo: IProductRepository,
        modifier_repo: IModifierRepository,
        tax_rate_repo: ITaxRateRepository,
        audit_service: IAuditLogService,
        actor_user_id: UUID,
    ) -> None:
        self._order_repo = order_repo
        self._product_repo = product_repo
        self._modifier_repo = modifier_repo
        self._tax_rate_repo = tax_rate_repo
        self._audit = audit_service
        self._actor = actor_user_id

    def execute(self, input_data: AddOrderItemInput) -> OrderItem:
        order = self._order_repo.find_by_id(input_data.order_id)
        if order is None:
            raise OrderNotFoundError(f"Order {input_data.order_id} not found")
        if not order.is_open():
            raise OrderAlreadyClosedError(
                f"Order {input_data.order_id} is {order.status.value} and cannot be modified"
            )

        product = self._product_repo.find_by_id(input_data.product_id)
        if product is None:
            raise ProductNotFoundError(f"Product {input_data.product_id} not found")

        # Tax rate resolution: product's explicit rate → fallback to default
        if product.tax_rate_id is not None:
            tax_rate = self._tax_rate_repo.find_by_id(product.tax_rate_id)
        else:
            tax_rate = self._tax_rate_repo.find_default()
        if tax_rate is None:
            raise DefaultTaxRateNotFoundError(
                "No default tax rate configured. Set a default tax rate before adding items."
            )

        item_id = uuid.uuid4()
        item = OrderItem(
            id=item_id,
            order_id=input_data.order_id,
            product_id=input_data.product_id,
            quantity=input_data.quantity,
            unit_price=product.base_price,
            applied_tax_rate=tax_rate.rate,
            status=OrderItemStatus.PENDING,
            notes=input_data.notes,
        )
        saved_item = self._order_repo.save_item(item)

        # Attach modifiers
        for modifier_id in input_data.modifier_ids:
            modifier = self._modifier_repo.find_by_id(modifier_id)
            if modifier is None:
                raise ModifierNotFoundError(f"Modifier {modifier_id} not found")
            item_modifier = OrderItemModifier(
                id=uuid.uuid4(),
                order_item_id=saved_item.id,
                modifier_id=modifier_id,
                applied_extra_price=modifier.extra_price,
            )
            saved_mod = self._order_repo.save_item_modifier(item_modifier)
            saved_item.modifiers.append(saved_mod)

        # Recalculate and persist order totals
        order.items = self._order_repo.find_items_by_order(order.id)
        # Replace the just-saved item with its full version (with modifiers)
        order.items = [
            saved_item if i.id == saved_item.id else i for i in order.items
        ]
        order.recalculate_totals()
        order.updated_at = datetime.now(timezone.utc)
        self._order_repo.update(order)

        self._audit.log(
            user_id=self._actor,
            action=AuditAction.ORDER_ITEM_ADDED,
            details={
                "order_id": str(input_data.order_id),
                "product_id": str(input_data.product_id),
                "quantity": input_data.quantity,
                "unit_price": str(product.base_price),
            },
        )
        return saved_item
