import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from app.domain.entities.reservation import Reservation, ReservationTable
from app.domain.enums import AuditAction, ReservationStatus, TableStatus
from app.domain.exceptions import (
    BranchNotFoundError,
    ReservationOverlapError,
    RestaurantTableNotFoundError,
    UserNotFoundError,
)
from app.domain.repositories.i_branch_repository import IBranchRepository
from app.domain.repositories.i_reservation_repository import IReservationRepository
from app.domain.repositories.i_restaurant_table_repository import IRestaurantTableRepository
from app.domain.repositories.i_system_config_repository import ISystemConfigRepository
from app.domain.repositories.i_user_repository import IUserRepository
from app.domain.services.i_audit_log_service import IAuditLogService

_DEFAULT_THRESHOLD_MINUTES = 30


@dataclass
class CreateReservationInput:
    branch_id: UUID
    created_by_user_id: UUID
    guest_name: str
    party_size: int
    scheduled_at: datetime
    table_ids: list[UUID] = field(default_factory=list)
    duration_minutes: int = 90
    guest_phone: Optional[str] = None
    notes: Optional[str] = None


class CreateReservationUseCase:
    def __init__(
        self,
        reservation_repo: IReservationRepository,
        table_repo: IRestaurantTableRepository,
        branch_repo: IBranchRepository,
        user_repo: IUserRepository,
        config_repo: ISystemConfigRepository,
        audit_service: IAuditLogService,
        actor_user_id: UUID,
    ) -> None:
        self._reservation_repo = reservation_repo
        self._table_repo = table_repo
        self._branch_repo = branch_repo
        self._user_repo = user_repo
        self._config_repo = config_repo
        self._audit = audit_service
        self._actor = actor_user_id

    def execute(self, input_data: CreateReservationInput) -> Reservation:
        # Validate branch
        branch = self._branch_repo.find_by_id(input_data.branch_id)
        if branch is None or not branch.is_active:
            raise BranchNotFoundError(f"Branch {input_data.branch_id} not found or inactive")

        # Validate creator
        creator = self._user_repo.find_by_id(input_data.created_by_user_id)
        if creator is None or not creator.is_active:
            raise UserNotFoundError(
                f"User {input_data.created_by_user_id} not found or inactive"
            )

        # Validate tables
        for table_id in input_data.table_ids:
            table = self._table_repo.find_by_id(table_id)
            if table is None:
                raise RestaurantTableNotFoundError(f"Table {table_id} not found")
            if table.branch_id != input_data.branch_id:
                raise RestaurantTableNotFoundError(
                    f"Table {table_id} does not belong to branch {input_data.branch_id}"
                )

        # Overlap check
        window_start = input_data.scheduled_at
        window_end = window_start + timedelta(minutes=input_data.duration_minutes)
        if input_data.table_ids:
            overlapping = self._reservation_repo.find_confirmed_overlapping(
                table_ids=input_data.table_ids,
                window_start=window_start,
                window_end=window_end,
            )
            if overlapping:
                raise ReservationOverlapError(
                    "One or more tables are already reserved in the requested time slot"
                )

        now = datetime.now(timezone.utc)
        reservation = Reservation(
            id=uuid.uuid4(),
            branch_id=input_data.branch_id,
            created_by_user_id=input_data.created_by_user_id,
            guest_name=input_data.guest_name,
            party_size=input_data.party_size,
            scheduled_at=input_data.scheduled_at,
            duration_minutes=input_data.duration_minutes,
            status=ReservationStatus.CONFIRMED,
            created_at=now,
            updated_at=now,
            order_id=None,
            guest_phone=input_data.guest_phone,
            notes=input_data.notes,
        )
        saved = self._reservation_repo.save(reservation)

        # Attach tables
        for table_id in input_data.table_ids:
            rt = ReservationTable(reservation_id=saved.id, table_id=table_id)
            self._reservation_repo.add_reservation_table(rt)

        # Conditionally mark tables RESERVED if within threshold
        threshold = self._get_threshold_minutes()
        minutes_until = (input_data.scheduled_at - now).total_seconds() / 60
        if 0 <= minutes_until <= threshold:
            for table_id in input_data.table_ids:
                self._table_repo.update_status(table_id, TableStatus.RESERVED)

        self._audit.log(
            user_id=self._actor,
            action=AuditAction.RESERVATION_CREATED,
            details={
                "reservation_id": str(saved.id),
                "table_ids": [str(t) for t in input_data.table_ids],
                "guest_name": input_data.guest_name,
                "scheduled_at": input_data.scheduled_at.isoformat(),
            },
        )
        saved.tables = self._reservation_repo.find_tables_by_reservation(saved.id)
        return saved

    def _get_threshold_minutes(self) -> int:
        config = self._config_repo.find_by_key("reservation_upcoming_threshold_minutes")
        if config is None:
            return _DEFAULT_THRESHOLD_MINUTES
        try:
            return int(config.value)
        except ValueError:
            return _DEFAULT_THRESHOLD_MINUTES
