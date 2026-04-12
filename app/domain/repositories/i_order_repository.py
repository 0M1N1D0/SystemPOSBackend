from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from app.domain.entities.order import Order, OrderItem, OrderItemModifier, OrderTable
from app.domain.enums import OrderStatus


class IOrderRepository(ABC):

    @abstractmethod
    def save(self, order: Order) -> Order: ...

    @abstractmethod
    def find_by_id(self, order_id: UUID) -> Optional[Order]: ...

    @abstractmethod
    def find_by_status(self, status: OrderStatus) -> list[Order]: ...

    @abstractmethod
    def update(self, order: Order) -> Order: ...

    # --- OrderTable ---

    @abstractmethod
    def add_order_table(self, order_table: OrderTable) -> None: ...

    @abstractmethod
    def remove_order_table(self, order_id: UUID, table_id: UUID) -> None: ...

    @abstractmethod
    def find_tables_by_order(self, order_id: UUID) -> list[OrderTable]: ...

    # --- OrderItem ---

    @abstractmethod
    def save_item(self, item: OrderItem) -> OrderItem: ...

    @abstractmethod
    def find_item_by_id(self, item_id: UUID) -> Optional[OrderItem]: ...

    @abstractmethod
    def update_item(self, item: OrderItem) -> OrderItem: ...

    @abstractmethod
    def find_items_by_order(self, order_id: UUID) -> list[OrderItem]: ...

    # --- OrderItemModifier ---

    @abstractmethod
    def save_item_modifier(self, modifier: OrderItemModifier) -> OrderItemModifier: ...

    @abstractmethod
    def find_modifiers_by_item(self, item_id: UUID) -> list[OrderItemModifier]: ...
