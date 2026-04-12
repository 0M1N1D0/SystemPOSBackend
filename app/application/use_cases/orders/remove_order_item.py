from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

from app.domain.enums import AuditAction, OrderItemStatus
from app.domain.exceptions import (
    OrderAlreadyClosedError,
    OrderItemNotFoundError,
    OrderNotFoundError,
)
from app.domain.repositories.i_order_repository import IOrderRepository
from app.domain.services.i_audit_log_service import IAuditLogService


@dataclass
class RemoveOrderItemInput:
    order_id: UUID
    item_id: UUID


class RemoveOrderItemUseCase:
    def __init__(
        self,
        order_repo: IOrderRepository,
        audit_service: IAuditLogService,
        actor_user_id: UUID,
    ) -> None:
        self._order_repo = order_repo
        self._audit = audit_service
        self._actor = actor_user_id

    def execute(self, input_data: RemoveOrderItemInput) -> None:
        order = self._order_repo.find_by_id(input_data.order_id)
        if order is None:
            raise OrderNotFoundError(f"Order {input_data.order_id} not found")
        if not order.is_open():
            raise OrderAlreadyClosedError(
                f"Order {input_data.order_id} is {order.status.value} and cannot be modified"
            )

        item = self._order_repo.find_item_by_id(input_data.item_id)
        if item is None or item.order_id != input_data.order_id:
            raise OrderItemNotFoundError(f"Item {input_data.item_id} not found in this order")

        item.status = OrderItemStatus.CANCELLED
        self._order_repo.update_item(item)

        # Recalculate order totals (CANCELLED items are excluded)
        order.items = self._order_repo.find_items_by_order(order.id)
        for existing in order.items:
            if existing.id == item.id:
                existing.status = OrderItemStatus.CANCELLED
        order.recalculate_totals()
        order.updated_at = datetime.now(timezone.utc)
        self._order_repo.update(order)

        self._audit.log(
            user_id=self._actor,
            action=AuditAction.ORDER_ITEM_REMOVED,
            details={
                "order_id": str(input_data.order_id),
                "order_item_id": str(input_data.item_id),
                "product_id": str(item.product_id),
                "quantity": item.quantity,
            },
        )
