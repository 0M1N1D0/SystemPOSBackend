from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID

from app.domain.enums import ReservationStatus
from app.domain.exceptions import ReservationTerminalStateError


_TERMINAL_STATES = {
    ReservationStatus.SEATED,
    ReservationStatus.CANCELLED,
    ReservationStatus.NO_SHOW,
}


@dataclass
class ReservationTable:
    reservation_id: UUID
    table_id: UUID


@dataclass
class Reservation:
    id: UUID
    branch_id: UUID
    created_by_user_id: UUID
    guest_name: str
    party_size: int
    scheduled_at: datetime
    duration_minutes: int
    status: ReservationStatus
    created_at: datetime
    updated_at: datetime
    order_id: Optional[UUID] = None
    guest_phone: Optional[str] = None
    notes: Optional[str] = None
    tables: list[ReservationTable] = field(default_factory=list)

    def is_terminal(self) -> bool:
        return self.status in _TERMINAL_STATES

    def transition_to(self, new_status: ReservationStatus) -> None:
        """Validates and applies a state transition."""
        if self.is_terminal():
            raise ReservationTerminalStateError(
                f"Cannot transition reservation {self.id} from terminal state "
                f"'{self.status.value}' to '{new_status.value}'"
            )
        self.status = new_status
