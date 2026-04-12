from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from app.domain.entities.order import Order
from app.domain.enums import AuditAction, OrderStatus, PaymentMethod, TableStatus
from app.domain.exceptions import (
    OrderAlreadyClosedError,
    OrderNotFoundError,
)
from app.domain.repositories.i_order_repository import IOrderRepository
from app.domain.repositories.i_restaurant_table_repository import IRestaurantTableRepository
from app.domain.services.i_audit_log_service import IAuditLogService


@dataclass
class PayOrderInput:
    order_id: UUID
    payment_method: PaymentMethod
    tip: Decimal = Decimal("0")


class PayOrderUseCase:
    def __init__(
        self,
        order_repo: IOrderRepository,
        table_repo: IRestaurantTableRepository,
        audit_service: IAuditLogService,
        actor_user_id: UUID,
    ) -> None:
        self._order_repo = order_repo
        self._table_repo = table_repo
        self._audit = audit_service
        self._actor = actor_user_id

    def execute(self, input_data: PayOrderInput) -> Order:
        order = self._order_repo.find_by_id(input_data.order_id)
        if order is None:
            raise OrderNotFoundError(f"Order {input_data.order_id} not found")
        if not order.is_open():
            raise OrderAlreadyClosedError(
                f"Order {input_data.order_id} is already {order.status.value}"
            )

        # Apply tip and recalculate
        order.tip = input_data.tip
        order.items = self._order_repo.find_items_by_order(order.id)
        order.recalculate_totals()

        order.payment_method = input_data.payment_method
        order.status = OrderStatus.PAID
        order.updated_at = datetime.now(timezone.utc)
        paid_order = self._order_repo.update(order)

        # Release all tables
        order_tables = self._order_repo.find_tables_by_order(order.id)
        for order_table in order_tables:
            table = self._table_repo.find_by_id(order_table.table_id)
            if table is not None:
                table.status = TableStatus.FREE
                self._table_repo.update(table)

        self._audit.log(
            user_id=self._actor,
            action=AuditAction.ORDER_PAID,
            details={
                "order_id": str(input_data.order_id),
                "total_amount": str(paid_order.total_amount),
                "payment_method": input_data.payment_method.value,
            },
        )
        paid_order.tables = order_tables
        paid_order.items = order.items
        return paid_order
