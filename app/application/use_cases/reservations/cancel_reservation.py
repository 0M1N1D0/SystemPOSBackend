from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from app.domain.enums import AuditAction, ReservationStatus, TableStatus
from app.domain.exceptions import ReservationNotFoundError, ReservationTerminalStateError
from app.domain.repositories.i_reservation_repository import IReservationRepository
from app.domain.repositories.i_restaurant_table_repository import IRestaurantTableRepository
from app.domain.services.i_audit_log_service import IAuditLogService


@dataclass
class CancelReservationInput:
    reservation_id: UUID
    reason: Optional[str] = None


class CancelReservationUseCase:
    def __init__(
        self,
        reservation_repo: IReservationRepository,
        table_repo: IRestaurantTableRepository,
        audit_service: IAuditLogService,
        actor_user_id: UUID,
    ) -> None:
        self._reservation_repo = reservation_repo
        self._table_repo = table_repo
        self._audit = audit_service
        self._actor = actor_user_id

    def execute(self, input_data: CancelReservationInput) -> None:
        reservation = self._reservation_repo.find_by_id(input_data.reservation_id)
        if reservation is None:
            raise ReservationNotFoundError(f"Reservation {input_data.reservation_id} not found")

        reservation.transition_to(ReservationStatus.CANCELLED)
        reservation.updated_at = datetime.now(timezone.utc)
        self._reservation_repo.update(reservation)

        # Reevaluate table status: free tables that have no other upcoming reservations
        now = datetime.now(timezone.utc)
        table_ids = [rt.table_id for rt in reservation.tables]
        for table_id in table_ids:
            upcoming = self._reservation_repo.find_confirmed_reservations_for_tables(
                table_ids=[table_id],
                after=now,
            )
            if not upcoming:
                self._table_repo.update_status(table_id, TableStatus.FREE)

        self._audit.log(
            user_id=self._actor,
            action=AuditAction.RESERVATION_CANCELLED,
            details={
                "reservation_id": str(reservation.id),
                "guest_name": reservation.guest_name,
                "reason": input_data.reason or "",
            },
        )
