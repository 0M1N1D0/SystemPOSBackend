import uuid
from datetime import timezone

from app.domain.entities.order import Order, OrderItem, OrderItemModifier, OrderTable
from app.domain.enums import OrderItemStatus, OrderStatus, PaymentMethod
from app.infrastructure.orm.order import (
    OrderItemModifierORM,
    OrderItemORM,
    OrderORM,
    OrderTableORM,
)


def order_to_domain(orm: OrderORM) -> Order:
    return Order(
        id=uuid.UUID(orm.id),
        user_id=uuid.UUID(orm.user_id),
        subtotal=orm.subtotal,
        taxes=orm.taxes,
        tip=orm.tip,
        discount=orm.discount,
        total_amount=orm.total_amount,
        status=OrderStatus(orm.status),
        payment_method=PaymentMethod(orm.payment_method) if orm.payment_method else None,
        created_at=orm.created_at.replace(tzinfo=timezone.utc)
        if orm.created_at.tzinfo is None
        else orm.created_at,
        updated_at=orm.updated_at.replace(tzinfo=timezone.utc)
        if orm.updated_at.tzinfo is None
        else orm.updated_at,
    )


def order_to_orm(entity: Order) -> OrderORM:
    return OrderORM(
        id=str(entity.id),
        user_id=str(entity.user_id),
        subtotal=entity.subtotal,
        taxes=entity.taxes,
        tip=entity.tip,
        discount=entity.discount,
        total_amount=entity.total_amount,
        status=entity.status.value,
        payment_method=entity.payment_method.value if entity.payment_method else None,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


def order_table_to_domain(orm: OrderTableORM) -> OrderTable:
    return OrderTable(
        order_id=uuid.UUID(orm.order_id),
        table_id=uuid.UUID(orm.table_id),
        joined_at=orm.joined_at.replace(tzinfo=timezone.utc)
        if orm.joined_at.tzinfo is None
        else orm.joined_at,
    )


def order_table_to_orm(entity: OrderTable) -> OrderTableORM:
    return OrderTableORM(
        order_id=str(entity.order_id),
        table_id=str(entity.table_id),
        joined_at=entity.joined_at,
    )


def order_item_to_domain(orm: OrderItemORM) -> OrderItem:
    return OrderItem(
        id=uuid.UUID(orm.id),
        order_id=uuid.UUID(orm.order_id),
        product_id=uuid.UUID(orm.product_id),
        quantity=orm.quantity,
        unit_price=orm.unit_price,
        applied_tax_rate=orm.applied_tax_rate,
        status=OrderItemStatus(orm.status),
        notes=orm.notes,
    )


def order_item_to_orm(entity: OrderItem) -> OrderItemORM:
    return OrderItemORM(
        id=str(entity.id),
        order_id=str(entity.order_id),
        product_id=str(entity.product_id),
        quantity=entity.quantity,
        unit_price=entity.unit_price,
        applied_tax_rate=entity.applied_tax_rate,
        status=entity.status.value,
        notes=entity.notes,
    )


def order_item_modifier_to_domain(orm: OrderItemModifierORM) -> OrderItemModifier:
    return OrderItemModifier(
        id=uuid.UUID(orm.id),
        order_item_id=uuid.UUID(orm.order_item_id),
        modifier_id=uuid.UUID(orm.modifier_id),
        applied_extra_price=orm.applied_extra_price,
    )


def order_item_modifier_to_orm(entity: OrderItemModifier) -> OrderItemModifierORM:
    return OrderItemModifierORM(
        id=str(entity.id),
        order_item_id=str(entity.order_item_id),
        modifier_id=str(entity.modifier_id),
        applied_extra_price=entity.applied_extra_price,
    )
