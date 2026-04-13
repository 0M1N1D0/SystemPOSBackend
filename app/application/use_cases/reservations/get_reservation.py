from uuid import UUID

from app.domain.entities.reservation import Reservation
from app.domain.exceptions import ReservationNotFoundError
from app.domain.repositories.i_reservation_repository import IReservationRepository


class GetReservationUseCase:
    def __init__(self, reservation_repo: IReservationRepository) -> None:
        self._reservation_repo = reservation_repo

    def execute(self, reservation_id: UUID) -> Reservation:
        reservation = self._reservation_repo.find_by_id(reservation_id)
        if reservation is None:
            raise ReservationNotFoundError(f"Reservation {reservation_id} not found")
        return reservation
