from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
from uuid import UUID

from app.domain.entities.reservation import Reservation, ReservationTable


class IReservationRepository(ABC):

    @abstractmethod
    def save(self, reservation: Reservation) -> Reservation: ...

    @abstractmethod
    def find_by_id(self, reservation_id: UUID) -> Optional[Reservation]: ...

    @abstractmethod
    def find_by_branch_and_date(
        self,
        branch_id: UUID,
        date_from: datetime,
        date_to: datetime,
    ) -> list[Reservation]: ...

    @abstractmethod
    def find_confirmed_overlapping(
        self,
        table_ids: list[UUID],
        window_start: datetime,
        window_end: datetime,
        exclude_reservation_id: Optional[UUID] = None,
    ) -> list[Reservation]: ...

    @abstractmethod
    def update(self, reservation: Reservation) -> Reservation: ...

    # --- ReservationTable ---

    @abstractmethod
    def add_reservation_table(self, reservation_table: ReservationTable) -> None: ...

    @abstractmethod
    def remove_reservation_tables(self, reservation_id: UUID) -> None: ...

    @abstractmethod
    def find_tables_by_reservation(self, reservation_id: UUID) -> list[ReservationTable]: ...

    @abstractmethod
    def find_confirmed_reservations_for_tables(
        self,
        table_ids: list[UUID],
        after: datetime,
    ) -> list[Reservation]: ...
