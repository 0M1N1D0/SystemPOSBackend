from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

from app.domain.enums import AuditAction, ReservationStatus, TableStatus
from app.domain.exceptions import ReservationNotFoundError
from app.domain.repositories.i_reservation_repository import IReservationRepository
from app.domain.repositories.i_restaurant_table_repository import IRestaurantTableRepository
from app.domain.services.i_audit_log_service import IAuditLogService


@dataclass
class MarkNoShowInput:
    reservation_id: UUID


class MarkNoShowUseCase:
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

    def execute(self, input_data: MarkNoShowInput) -> None:
        reservation = self._reservation_repo.find_by_id(input_data.reservation_id)
        if reservation is None:
            raise ReservationNotFoundError(f"Reservation {input_data.reservation_id} not found")

        reservation.transition_to(ReservationStatus.NO_SHOW)
        reservation.updated_at = datetime.now(timezone.utc)
        self._reservation_repo.update(reservation)

        # Free all reserved tables
        table_ids = [rt.table_id for rt in reservation.tables]
        for table_id in table_ids:
            self._table_repo.update_status(table_id, TableStatus.FREE)

        self._audit.log(
            user_id=self._actor,
            action=AuditAction.RESERVATION_NO_SHOW,
            details={
                "reservation_id": str(reservation.id),
                "guest_name": reservation.guest_name,
                "scheduled_at": reservation.scheduled_at.isoformat(),
            },
        )
