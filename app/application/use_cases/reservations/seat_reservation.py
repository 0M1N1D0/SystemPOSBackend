import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from app.domain.entities.order import Order, OrderTable
from app.domain.enums import AuditAction, OrderStatus, ReservationStatus, TableStatus
from app.domain.exceptions import ReservationNotFoundError, ReservationTerminalStateError
from app.domain.repositories.i_order_repository import IOrderRepository
from app.domain.repositories.i_reservation_repository import IReservationRepository
from app.domain.repositories.i_restaurant_table_repository import IRestaurantTableRepository
from app.domain.services.i_audit_log_service import IAuditLogService


@dataclass
class SeatReservationInput:
    reservation_id: UUID


class SeatReservationUseCase:
    def __init__(
        self,
        reservation_repo: IReservationRepository,
        order_repo: IOrderRepository,
        table_repo: IRestaurantTableRepository,
        audit_service: IAuditLogService,
        actor_user_id: UUID,
    ) -> None:
        self._reservation_repo = reservation_repo
        self._order_repo = order_repo
        self._table_repo = table_repo
        self._audit = audit_service
        self._actor = actor_user_id

    def execute(self, input_data: SeatReservationInput) -> Order:
        reservation = self._reservation_repo.find_by_id(input_data.reservation_id)
        if reservation is None:
            raise ReservationNotFoundError(f"Reservation {input_data.reservation_id} not found")

        reservation.transition_to(ReservationStatus.SEATED)

        now = datetime.now(timezone.utc)
        order_id = uuid.uuid4()

        # Open a new order assigned to the actor (the waiter seating the guest)
        order = Order(
            id=order_id,
            user_id=self._actor,
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

        # Link tables to the order and mark them OCCUPIED
        table_ids = [rt.table_id for rt in reservation.tables]
        for table_id in table_ids:
            order_table = OrderTable(
                order_id=saved_order.id,
                table_id=table_id,
                joined_at=now,
            )
            self._order_repo.add_order_table(order_table)
            self._table_repo.update_status(table_id, TableStatus.OCCUPIED)

        # Link order to reservation
        reservation.order_id = saved_order.id
        reservation.updated_at = now
        self._reservation_repo.update(reservation)

        self._audit.log(
            user_id=self._actor,
            action=AuditAction.RESERVATION_SEATED,
            details={
                "reservation_id": str(reservation.id),
                "order_id": str(saved_order.id),
                "table_ids": [str(t) for t in table_ids],
            },
        )
        saved_order.tables = self._order_repo.find_tables_by_order(saved_order.id)
        return saved_order
