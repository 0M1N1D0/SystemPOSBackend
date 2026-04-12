from app.domain.entities.order import Order
from app.domain.enums import OrderStatus
from app.domain.repositories.i_order_repository import IOrderRepository


class ListOpenOrdersUseCase:
    def __init__(self, order_repo: IOrderRepository) -> None:
        self._order_repo = order_repo

    def execute(self) -> list[Order]:
        orders = self._order_repo.find_by_status(OrderStatus.OPEN)
        for order in orders:
            order.items = self._order_repo.find_items_by_order(order.id)
            for item in order.items:
                item.modifiers = self._order_repo.find_modifiers_by_item(item.id)
            order.tables = self._order_repo.find_tables_by_order(order.id)
        return orders
