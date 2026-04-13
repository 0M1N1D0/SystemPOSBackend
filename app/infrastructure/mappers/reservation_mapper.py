import uuid
from datetime import timezone

from app.domain.entities.reservation import Reservation, ReservationTable
from app.domain.enums import ReservationStatus
from app.infrastructure.orm.reservation import ReservationORM, ReservationTableORM


def reservation_to_domain(orm: ReservationORM) -> Reservation:
    def _tz(dt):
        return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt

    return Reservation(
        id=uuid.UUID(orm.id),
        branch_id=uuid.UUID(orm.branch_id),
        created_by_user_id=uuid.UUID(orm.created_by_user_id),
        order_id=uuid.UUID(orm.order_id) if orm.order_id else None,
        guest_name=orm.guest_name,
        guest_phone=orm.guest_phone,
        party_size=orm.party_size,
        scheduled_at=_tz(orm.scheduled_at),
        duration_minutes=orm.duration_minutes,
        status=ReservationStatus(orm.status),
        notes=orm.notes,
        created_at=_tz(orm.created_at),
        updated_at=_tz(orm.updated_at),
    )


def reservation_to_orm(entity: Reservation) -> ReservationORM:
    return ReservationORM(
        id=str(entity.id),
        branch_id=str(entity.branch_id),
        created_by_user_id=str(entity.created_by_user_id),
        order_id=str(entity.order_id) if entity.order_id else None,
        guest_name=entity.guest_name,
        guest_phone=entity.guest_phone,
        party_size=entity.party_size,
        scheduled_at=entity.scheduled_at,
        duration_minutes=entity.duration_minutes,
        status=entity.status.value,
        notes=entity.notes,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


def reservation_table_to_domain(orm: ReservationTableORM) -> ReservationTable:
    return ReservationTable(
        reservation_id=uuid.UUID(orm.reservation_id),
        table_id=uuid.UUID(orm.table_id),
    )


def reservation_table_to_orm(entity: ReservationTable) -> ReservationTableORM:
    return ReservationTableORM(
        reservation_id=str(entity.reservation_id),
        table_id=str(entity.table_id),
    )
