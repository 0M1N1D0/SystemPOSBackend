import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from app.domain.entities.order import Order, OrderTable
from app.domain.enums import AuditAction, OrderStatus, TableStatus
from app.domain.exceptions import (
    OrderNotFoundError,
    RestaurantTableNotFoundError,
    TableAlreadyOccupiedError,
    UserNotFoundError,
)
from app.domain.repositories.i_order_repository import IOrderRepository
from app.domain.repositories.i_restaurant_table_repository import IRestaurantTableRepository
from app.domain.repositories.i_user_repository import IUserRepository
from app.domain.services.i_audit_log_service import IAuditLogService


@dataclass
class CreateOrderInput:
    waiter_user_id: UUID
    table_ids: list[UUID] = field(default_factory=list)


class CreateOrderUseCase:
    def __init__(
        self,
        order_repo: IOrderRepository,
        table_repo: IRestaurantTableRepository,
        user_repo: IUserRepository,
        audit_service: IAuditLogService,
        actor_user_id: UUID,
    ) -> None:
        self._order_repo = order_repo
        self._table_repo = table_repo
        self._user_repo = user_repo
        self._audit = audit_service
        self._actor = actor_user_id

    def execute(self, input_data: CreateOrderInput) -> Order:
        # Validate waiter exists and is active
        waiter = self._user_repo.find_by_id(input_data.waiter_user_id)
        if waiter is None or not waiter.is_active:
            raise UserNotFoundError(f"User {input_data.waiter_user_id} not found or inactive")

        # Validate tables exist and are FREE
        tables = []
        for table_id in input_data.table_ids:
            table = self._table_repo.find_by_id(table_id)
            if table is None:
                raise RestaurantTableNotFoundError(f"Table {table_id} not found")
            if table.status == TableStatus.OCCUPIED:
                raise TableAlreadyOccupiedError(
                    f"Table {table.identifier} is already occupied"
                )
            tables.append(table)

        now = datetime.now(timezone.utc)
        order_id = uuid.uuid4()

        order = Order(
            id=order_id,
            user_id=input_data.waiter_user_id,
            subtotal=Decimal("0"),
            taxes=Decimal("0"),
            tip=Decimal("0"),
            discount=Decimal("0"),
            total_amount=Decimal("0"),
            status=OrderStatus.OPEN,
            payment_method=None,
            created_at=now,
            updated_at=now,
        )
        saved_order = self._order_repo.save(order)

        # Assign tables and mark them OCCUPIED
        for table in tables:
            order_table = OrderTable(
                order_id=saved_order.id,
                table_id=table.id,
                joined_at=now,
            )
            self._order_repo.add_order_table(order_table)
            table.status = TableStatus.OCCUPIED
            self._table_repo.update(table)

        self._audit.log(
            user_id=self._actor,
            action=AuditAction.ORDER_CREATED,
            details={
                "order_id": str(saved_order.id),
                "waiter_user_id": str(input_data.waiter_user_id),
                "table_ids": [str(t) for t in input_data.table_ids],
            },
        )
        saved_order.tables = self._order_repo.find_tables_by_order(saved_order.id)
        return saved_order
