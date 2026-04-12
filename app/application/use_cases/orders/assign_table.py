from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

from app.domain.entities.order import OrderTable
from app.domain.enums import AuditAction, TableStatus
from app.domain.exceptions import (
    OrderAlreadyClosedError,
    OrderNotFoundError,
    RestaurantTableNotFoundError,
    TableAlreadyOccupiedError,
)
from app.domain.repositories.i_order_repository import IOrderRepository
from app.domain.repositories.i_restaurant_table_repository import IRestaurantTableRepository
from app.domain.services.i_audit_log_service import IAuditLogService


@dataclass
class AssignTableInput:
    order_id: UUID
    table_id: UUID


class AssignTableUseCase:
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

    def execute(self, input_data: AssignTableInput) -> None:
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
        if table.status == TableStatus.OCCUPIED:
            raise TableAlreadyOccupiedError(
                f"Table {table.identifier} is already occupied"
            )

        order_table = OrderTable(
            order_id=input_data.order_id,
            table_id=input_data.table_id,
            joined_at=datetime.now(timezone.utc),
        )
        self._order_repo.add_order_table(order_table)
        table.status = TableStatus.OCCUPIED
        self._table_repo.update(table)

        self._audit.log(
            user_id=self._actor,
            action=AuditAction.TABLE_ASSIGNED,
            details={
                "order_id": str(input_data.order_id),
                "table_id": str(input_data.table_id),
            },
        )
