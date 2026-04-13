from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from app.domain.entities.reservation import ReservationTable
from app.domain.enums import AuditAction, TableStatus
from app.domain.exceptions import (
    ReservationNotFoundError,
    ReservationOverlapError,
    ReservationTerminalStateError,
    RestaurantTableNotFoundError,
)
from app.domain.repositories.i_reservation_repository import IReservationRepository
from app.domain.repositories.i_restaurant_table_repository import IRestaurantTableRepository
from app.domain.repositories.i_system_config_repository import ISystemConfigRepository
from app.domain.services.i_audit_log_service import IAuditLogService

_DEFAULT_THRESHOLD_MINUTES = 30


@dataclass
class UpdateReservationInput:
    reservation_id: UUID
    guest_name: Optional[str] = None
    guest_phone: Optional[str] = None
    party_size: Optional[int] = None
    scheduled_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    notes: Optional[str] = None
    table_ids: Optional[list[UUID]] = None


class UpdateReservationUseCase:
    def __init__(
        self,
        reservation_repo: IReservationRepository,
        table_repo: IRestaurantTableRepository,
        config_repo: ISystemConfigRepository,
        audit_service: IAuditLogService,
        actor_user_id: UUID,
    ) -> None:
        self._reservation_repo = reservation_repo
        self._table_repo = table_repo
        self._config_repo = config_repo
        self._audit = audit_service
        self._actor = actor_user_id

    def execute(self, input_data: UpdateReservationInput) -> None:
        reservation = self._reservation_repo.find_by_id(input_data.reservation_id)
        if reservation is None:
            raise ReservationNotFoundError(f"Reservation {input_data.reservation_id} not found")
        if reservation.is_terminal():
            raise ReservationTerminalStateError(
                f"Cannot update reservation in terminal state '{reservation.status.value}'"
            )

        changed_fields: list[str] = []

        if input_data.guest_name is not None and input_data.guest_name != reservation.guest_name:
            reservation.guest_name = input_data.guest_name
            changed_fields.append("guest_name")
        if input_data.guest_phone is not None and input_data.guest_phone != reservation.guest_phone:
            reservation.guest_phone = input_data.guest_phone
            changed_fields.append("guest_phone")
        if input_data.party_size is not None and input_data.party_size != reservation.party_size:
            reservation.party_size = input_data.party_size
            changed_fields.append("party_size")
        if input_data.notes is not None and input_data.notes != reservation.notes:
            reservation.notes = input_data.notes
            changed_fields.append("notes")

        new_scheduled_at = input_data.scheduled_at or reservation.scheduled_at
        new_duration = input_data.duration_minutes or reservation.duration_minutes

        if input_data.scheduled_at is not None and input_data.scheduled_at != reservation.scheduled_at:
            reservation.scheduled_at = input_data.scheduled_at
            changed_fields.append("scheduled_at")
        if input_data.duration_minutes is not None and input_data.duration_minutes != reservation.duration_minutes:
            reservation.duration_minutes = input_data.duration_minutes
            changed_fields.append("duration_minutes")

        # Re-assign tables if provided
        current_table_ids = [rt.table_id for rt in reservation.tables]
        if input_data.table_ids is not None and set(input_data.table_ids) != set(current_table_ids):
            # Validate new tables
            for table_id in input_data.table_ids:
                table = self._table_repo.find_by_id(table_id)
                if table is None:
                    raise RestaurantTableNotFoundError(f"Table {table_id} not found")
                if table.branch_id != reservation.branch_id:
                    raise RestaurantTableNotFoundError(
                        f"Table {table_id} does not belong to the reservation's branch"
                    )

            # Overlap check with new tables/window
            window_start = new_scheduled_at
            window_end = window_start + timedelta(minutes=new_duration)
            if input_data.table_ids:
                overlapping = self._reservation_repo.find_confirmed_overlapping(
                    table_ids=input_data.table_ids,
                    window_start=window_start,
                    window_end=window_end,
                    exclude_reservation_id=reservation.id,
                )
                if overlapping:
                    raise ReservationOverlapError(
                        "One or more tables are already reserved in the requested time slot"
                    )

            # Release old tables if not in new list
            old_reserved = set(current_table_ids) - set(input_data.table_ids)
            for table_id in old_reserved:
                upcoming = self._reservation_repo.find_confirmed_reservations_for_tables(
                    table_ids=[table_id],
                    after=datetime.now(timezone.utc),
                )
                if not upcoming:
                    self._table_repo.update_status(table_id, TableStatus.FREE)

            # Remove all old join rows and re-add
            self._reservation_repo.remove_reservation_tables(reservation.id)
            for table_id in input_data.table_ids:
                self._reservation_repo.add_reservation_table(
                    ReservationTable(reservation_id=reservation.id, table_id=table_id)
                )
            changed_fields.append("table_ids")

            # Reapply RESERVED status if within threshold
            threshold = self._get_threshold_minutes()
            now = datetime.now(timezone.utc)
            minutes_until = (new_scheduled_at - now).total_seconds() / 60
            if 0 <= minutes_until <= threshold:
                for table_id in input_data.table_ids:
                    self._table_repo.update_status(table_id, TableStatus.RESERVED)

        reservation.updated_at = datetime.now(timezone.utc)
        self._reservation_repo.update(reservation)

        if changed_fields:
            self._audit.log(
                user_id=self._actor,
                action=AuditAction.RESERVATION_UPDATED,
                details={
                    "reservation_id": str(reservation.id),
                    "changed_fields": changed_fields,
                },
            )

    def _get_threshold_minutes(self) -> int:
        config = self._config_repo.find_by_key("reservation_upcoming_threshold_minutes")
        if config is None:
            return _DEFAULT_THRESHOLD_MINUTES
        try:
            return int(config.value)
        except ValueError:
            return _DEFAULT_THRESHOLD_MINUTES
