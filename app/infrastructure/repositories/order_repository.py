from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.entities.order import Order, OrderItem, OrderItemModifier, OrderTable
from app.domain.enums import OrderStatus
from app.domain.repositories.i_order_repository import IOrderRepository
from app.infrastructure.mappers import order_mapper
from app.infrastructure.orm.order import (
    OrderItemModifierORM,
    OrderItemORM,
    OrderORM,
    OrderTableORM,
)


class SqlOrderRepository(IOrderRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    # --- Order ---

    def save(self, order: Order) -> Order:
        orm = order_mapper.order_to_orm(order)
        self._session.add(orm)
        self._session.commit()
        self._session.refresh(orm)
        return order_mapper.order_to_domain(orm)

    def find_by_id(self, order_id: UUID) -> Optional[Order]:
        orm = self._session.get(OrderORM, str(order_id))
        return order_mapper.order_to_domain(orm) if orm else None

    def find_by_status(self, status: OrderStatus) -> list[Order]:
        rows = (
            self._session.query(OrderORM)
            .filter(OrderORM.status == status.value)
            .order_by(OrderORM.created_at.desc())
            .all()
        )
        return [order_mapper.order_to_domain(r) for r in rows]

    def update(self, order: Order) -> Order:
        orm = self._session.get(OrderORM, str(order.id))
        orm.subtotal = order.subtotal
        orm.taxes = order.taxes
        orm.tip = order.tip
        orm.discount = order.discount
        orm.total_amount = order.total_amount
        orm.status = order.status.value
        orm.payment_method = order.payment_method.value if order.payment_method else None
        orm.updated_at = order.updated_at
        self._session.commit()
        self._session.refresh(orm)
        return order_mapper.order_to_domain(orm)

    # --- OrderTable ---

    def add_order_table(self, order_table: OrderTable) -> None:
        orm = order_mapper.order_table_to_orm(order_table)
        self._session.add(orm)
        self._session.commit()

    def remove_order_table(self, order_id: UUID, table_id: UUID) -> None:
        orm = self._session.get(OrderTableORM, (str(order_id), str(table_id)))
        if orm:
            self._session.delete(orm)
            self._session.commit()

    def find_tables_by_order(self, order_id: UUID) -> list[OrderTable]:
        rows = (
            self._session.query(OrderTableORM)
            .filter(OrderTableORM.order_id == str(order_id))
            .all()
        )
        return [order_mapper.order_table_to_domain(r) for r in rows]

    # --- OrderItem ---

    def save_item(self, item: OrderItem) -> OrderItem:
        orm = order_mapper.order_item_to_orm(item)
        self._session.add(orm)
        self._session.commit()
        self._session.refresh(orm)
        return order_mapper.order_item_to_domain(orm)

    def find_item_by_id(self, item_id: UUID) -> Optional[OrderItem]:
        orm = self._session.get(OrderItemORM, str(item_id))
        return order_mapper.order_item_to_domain(orm) if orm else None

    def update_item(self, item: OrderItem) -> OrderItem:
        orm = self._session.get(OrderItemORM, str(item.id))
        orm.quantity = item.quantity
        orm.status = item.status.value
        orm.notes = item.notes
        self._session.commit()
        self._session.refresh(orm)
        return order_mapper.order_item_to_domain(orm)

    def find_items_by_order(self, order_id: UUID) -> list[OrderItem]:
        rows = (
            self._session.query(OrderItemORM)
            .filter(OrderItemORM.order_id == str(order_id))
            .all()
        )
        return [order_mapper.order_item_to_domain(r) for r in rows]

    # --- OrderItemModifier ---

    def save_item_modifier(self, modifier: OrderItemModifier) -> OrderItemModifier:
        orm = order_mapper.order_item_modifier_to_orm(modifier)
        self._session.add(orm)
        self._session.commit()
        self._session.refresh(orm)
        return order_mapper.order_item_modifier_to_domain(orm)

    def find_modifiers_by_item(self, item_id: UUID) -> list[OrderItemModifier]:
        rows = (
            self._session.query(OrderItemModifierORM)
            .filter(OrderItemModifierORM.order_item_id == str(item_id))
            .all()
        )
        return [order_mapper.order_item_modifier_to_domain(r) for r in rows]
