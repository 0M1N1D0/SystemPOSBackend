from dataclasses import dataclass
from uuid import UUID

from app.domain.enums import AuditAction, TableStatus
from app.domain.exceptions import (
    BusinessRuleViolationError,
    OrderAlreadyClosedError,
    OrderNotFoundError,
    RestaurantTableNotFoundError,
)
from app.domain.repositories.i_order_repository import IOrderRepository
from app.domain.repositories.i_restaurant_table_repository import IRestaurantTableRepository
from app.domain.services.i_audit_log_service import IAuditLogService


@dataclass
class ReleaseTableInput:
    order_id: UUID
    table_id: UUID


class ReleaseTableUseCase:
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

    def execute(self, input_data: ReleaseTableInput) -> None:
        order = self._order_repo.find_by_id(input_data.order_id)
        if order is None:
            raise OrderNotFoundError(f"Order {input_data.order_id} not found")
        if not order.is_open():
            raise OrderAlreadyClosedError(
                f"Order {input_data.order_id} is {order.status.value}"
            )

        table = self._table_repo.find_by_id(input_data.table_id)
        if table is None:
            raise RestaurantTableNotFoundError(f"Table {input_data.table_id} not found")

        order_tables = self._order_repo.find_tables_by_order(input_data.order_id)
        if not any(ot.table_id == input_data.table_id for ot in order_tables):
            raise BusinessRuleViolationError(
                f"Table {input_data.table_id} is not assigned to order {input_data.order_id}"
            )
        if len(order_tables) <= 1:
            raise BusinessRuleViolationError(
                "Cannot release the last table from an open order"
            )

        self._order_repo.remove_order_table(input_data.order_id, input_data.table_id)
        table.status = TableStatus.FREE
        self._table_repo.update(table)

        self._audit.log(
            user_id=self._actor,
            action=AuditAction.TABLE_RELEASED,
            details={
                "order_id": str(input_data.order_id),
                "table_id": str(input_data.table_id),
            },
        )
