from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import and_, exists, select
from sqlalchemy.orm import Session

from app.domain.entities.reservation import Reservation, ReservationTable
from app.domain.enums import ReservationStatus
from app.domain.repositories.i_reservation_repository import IReservationRepository
from app.infrastructure.mappers import reservation_mapper
from app.infrastructure.orm.reservation import ReservationORM, ReservationTableORM


class SqlReservationRepository(IReservationRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, reservation: Reservation) -> Reservation:
        orm = reservation_mapper.reservation_to_orm(reservation)
        self._session.add(orm)
        self._session.commit()
        self._session.refresh(orm)
        return reservation_mapper.reservation_to_domain(orm)

    def find_by_id(self, reservation_id: UUID) -> Optional[Reservation]:
        orm = self._session.get(ReservationORM, str(reservation_id))
        if orm is None:
            return None
        reservation = reservation_mapper.reservation_to_domain(orm)
        reservation.tables = self.find_tables_by_reservation(reservation_id)
        return reservation

    def find_by_branch_and_date(
        self,
        branch_id: UUID,
        date_from: datetime,
        date_to: datetime,
    ) -> list[Reservation]:
        rows = (
            self._session.query(ReservationORM)
            .filter(
                ReservationORM.branch_id == str(branch_id),
                ReservationORM.scheduled_at >= date_from,
                ReservationORM.scheduled_at <= date_to,
            )
            .order_by(ReservationORM.scheduled_at)
            .all()
        )
        result = []
        for row in rows:
            r = reservation_mapper.reservation_to_domain(row)
            r.tables = self.find_tables_by_reservation(r.id)
            result.append(r)
        return result

    def find_confirmed_overlapping(
        self,
        table_ids: list[UUID],
        window_start: datetime,
        window_end: datetime,
        exclude_reservation_id: Optional[UUID] = None,
    ) -> list[Reservation]:
        """
        Returns CONFIRMED reservations that overlap [window_start, window_end)
        for any of the given table_ids.
        Overlap condition: existing.scheduled_at < window_end
                       AND existing.scheduled_at + duration > window_start
        """
        from sqlalchemy import func, cast
        from sqlalchemy.dialects.postgresql import INTERVAL

        str_ids = [str(t) for t in table_ids]

        # Subquery: reservation IDs that touch any of the given tables
        table_sub = (
            select(ReservationTableORM.reservation_id)
            .where(ReservationTableORM.table_id.in_(str_ids))
            .scalar_subquery()
        )

        query = self._session.query(ReservationORM).filter(
            ReservationORM.status == ReservationStatus.CONFIRMED.value,
            ReservationORM.id.in_(table_sub),
            ReservationORM.scheduled_at < window_end,
            # scheduled_at + interval > window_start
            ReservationORM.scheduled_at
            + func.cast(
                func.concat(ReservationORM.duration_minutes, " minutes"),
                INTERVAL,
            )
            > window_start,
        )
        if exclude_reservation_id is not None:
            query = query.filter(ReservationORM.id != str(exclude_reservation_id))

        return [reservation_mapper.reservation_to_domain(r) for r in query.all()]

    def update(self, reservation: Reservation) -> Reservation:
        orm = self._session.get(ReservationORM, str(reservation.id))
        orm.order_id = str(reservation.order_id) if reservation.order_id else None
        orm.guest_name = reservation.guest_name
        orm.guest_phone = reservation.guest_phone
        orm.party_size = reservation.party_size
        orm.scheduled_at = reservation.scheduled_at
        orm.duration_minutes = reservation.duration_minutes
        orm.status = reservation.status.value
        orm.notes = reservation.notes
        orm.updated_at = reservation.updated_at
        self._session.commit()
        self._session.refresh(orm)
        updated = reservation_mapper.reservation_to_domain(orm)
        updated.tables = self.find_tables_by_reservation(reservation.id)
        return updated

    # --- ReservationTable ---

    def add_reservation_table(self, reservation_table: ReservationTable) -> None:
        orm = reservation_mapper.reservation_table_to_orm(reservation_table)
        self._session.add(orm)
        self._session.commit()

    def remove_reservation_tables(self, reservation_id: UUID) -> None:
        self._session.query(ReservationTableORM).filter(
            ReservationTableORM.reservation_id == str(reservation_id)
        ).delete()
        self._session.commit()

    def find_tables_by_reservation(self, reservation_id: UUID) -> list[ReservationTable]:
        rows = (
            self._session.query(ReservationTableORM)
            .filter(ReservationTableORM.reservation_id == str(reservation_id))
            .all()
        )
        return [reservation_mapper.reservation_table_to_domain(r) for r in rows]

    def find_confirmed_reservations_for_tables(
        self,
        table_ids: list[UUID],
        after: datetime,
    ) -> list[Reservation]:
        str_ids = [str(t) for t in table_ids]
        table_sub = (
            select(ReservationTableORM.reservation_id)
            .where(ReservationTableORM.table_id.in_(str_ids))
            .scalar_subquery()
        )
        rows = (
            self._session.query(ReservationORM)
            .filter(
                ReservationORM.status == ReservationStatus.CONFIRMED.value,
                ReservationORM.id.in_(table_sub),
                ReservationORM.scheduled_at >= after,
            )
            .all()
        )
        return [reservation_mapper.reservation_to_domain(r) for r in rows]
