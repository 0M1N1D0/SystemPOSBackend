from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.entities.reservation import Reservation
from app.domain.exceptions import BranchNotFoundError
from app.domain.repositories.i_branch_repository import IBranchRepository
from app.domain.repositories.i_reservation_repository import IReservationRepository


@dataclass
class ListReservationsByBranchInput:
    branch_id: UUID
    date_from: datetime
    date_to: datetime


class ListReservationsByBranchUseCase:
    def __init__(
        self,
        reservation_repo: IReservationRepository,
        branch_repo: IBranchRepository,
    ) -> None:
        self._reservation_repo = reservation_repo
        self._branch_repo = branch_repo

    def execute(self, input_data: ListReservationsByBranchInput) -> list[Reservation]:
        branch = self._branch_repo.find_by_id(input_data.branch_id)
        if branch is None:
            raise BranchNotFoundError(f"Branch {input_data.branch_id} not found")
        return self._reservation_repo.find_by_branch_and_date(
            branch_id=input_data.branch_id,
            date_from=input_data.date_from,
            date_to=input_data.date_to,
        )
