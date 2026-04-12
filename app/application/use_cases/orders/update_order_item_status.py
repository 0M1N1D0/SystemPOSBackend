from dataclasses import dataclass
from uuid import UUID

from app.domain.entities.order import OrderItem
from app.domain.enums import OrderItemStatus
from app.domain.exceptions import (
    BusinessRuleViolationError,
    OrderAlreadyClosedError,
    OrderItemNotFoundError,
    OrderNotFoundError,
)
from app.domain.repositories.i_order_repository import IOrderRepository

# Valid KDS transitions: only forward movement is allowed
_VALID_TRANSITIONS: dict[OrderItemStatus, set[OrderItemStatus]] = {
    OrderItemStatus.PENDING: {OrderItemStatus.IN_PREPARATION, OrderItemStatus.CANCELLED},
    OrderItemStatus.IN_PREPARATION: {OrderItemStatus.READY, OrderItemStatus.CANCELLED},
    OrderItemStatus.READY: {OrderItemStatus.DELIVERED},
    OrderItemStatus.DELIVERED: set(),
    OrderItemStatus.CANCELLED: set(),
}


@dataclass
class UpdateOrderItemStatusInput:
    order_id: UUID
    item_id: UUID
    new_status: OrderItemStatus


class UpdateOrderItemStatusUseCase:
    def __init__(self, order_repo: IOrderRepository) -> None:
        self._order_repo = order_repo

    def execute(self, input_data: UpdateOrderItemStatusInput) -> OrderItem:
        order = self._order_repo.find_by_id(input_data.order_id)
        if order is None:
            raise OrderNotFoundError(f"Order {input_data.order_id} not found")
        if not order.is_open():
            raise OrderAlreadyClosedError(
                f"Order {input_data.order_id} is {order.status.value}"
            )

        item = self._order_repo.find_item_by_id(input_data.item_id)
        if item is None or item.order_id != input_data.order_id:
            raise OrderItemNotFoundError(f"Item {input_data.item_id} not found in this order")

        allowed = _VALID_TRANSITIONS.get(item.status, set())
        if input_data.new_status not in allowed:
            raise BusinessRuleViolationError(
                f"Cannot transition item from {item.status.value} to {input_data.new_status.value}"
            )

        item.status = input_data.new_status
        return self._order_repo.update_item(item)
