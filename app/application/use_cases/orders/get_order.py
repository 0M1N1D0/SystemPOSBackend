from uuid import UUID

from app.domain.entities.order import Order
from app.domain.exceptions import OrderNotFoundError
from app.domain.repositories.i_order_repository import IOrderRepository


class GetOrderUseCase:
    def __init__(self, order_repo: IOrderRepository) -> None:
        self._order_repo = order_repo

    def execute(self, order_id: UUID) -> Order:
        order = self._order_repo.find_by_id(order_id)
        if order is None:
            raise OrderNotFoundError(f"Order {order_id} not found")
        order.items = self._order_repo.find_items_by_order(order_id)
        for item in order.items:
            item.modifiers = self._order_repo.find_modifiers_by_item(item.id)
        order.tables = self._order_repo.find_tables_by_order(order_id)
        return order
