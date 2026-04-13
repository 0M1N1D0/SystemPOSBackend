from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.application.use_cases.reservations.cancel_reservation import (
    CancelReservationInput,
    CancelReservationUseCase,
)
from app.application.use_cases.reservations.create_reservation import (
    CreateReservationInput,
    CreateReservationUseCase,
)
from app.application.use_cases.reservations.get_reservation import GetReservationUseCase
from app.application.use_cases.reservations.list_reservations_by_branch import (
    ListReservationsByBranchInput,
    ListReservationsByBranchUseCase,
)
from app.application.use_cases.reservations.mark_no_show import (
    MarkNoShowInput,
    MarkNoShowUseCase,
)
from app.application.use_cases.reservations.seat_reservation import (
    SeatReservationInput,
    SeatReservationUseCase,
)
from app.application.use_cases.reservations.update_reservation import (
    UpdateReservationInput,
    UpdateReservationUseCase,
)
from app.domain.services.i_token_service import TokenPayload
from app.presentation.dependencies import (
    get_cancel_reservation_use_case,
    get_create_reservation_use_case,
    get_get_reservation_use_case,
    get_list_reservations_by_branch_use_case,
    get_mark_no_show_use_case,
    get_seat_reservation_use_case,
    get_update_reservation_use_case,
    get_current_token_payload,
)
from app.presentation.schemas.order import OrderResponse
from app.presentation.schemas.reservation import (
    CancelReservationRequest,
    CreateReservationRequest,
    ReservationResponse,
    ReservationTableResponse,
    UpdateReservationRequest,
)

router = APIRouter()


def _map_reservation(reservation) -> ReservationResponse:
    return ReservationResponse(
        id=reservation.id,
        branch_id=reservation.branch_id,
        created_by_user_id=reservation.created_by_user_id,
        order_id=reservation.order_id,
        guest_name=reservation.guest_name,
        guest_phone=reservation.guest_phone,
        party_size=reservation.party_size,
        scheduled_at=reservation.scheduled_at,
        duration_minutes=reservation.duration_minutes,
        status=reservation.status,
        notes=reservation.notes,
        created_at=reservation.created_at,
        updated_at=reservation.updated_at,
        tables=[ReservationTableResponse(table_id=rt.table_id) for rt in reservation.tables],
    )


@router.get("/", response_model=list[ReservationResponse])
def list_reservations_by_branch(
    branch_id: UUID = Query(...),
    date_from: datetime = Query(...),
    date_to: datetime = Query(...),
    use_case: ListReservationsByBranchUseCase = Depends(get_list_reservations_by_branch_use_case),
    _: TokenPayload = Depends(get_current_token_payload),
) -> list[ReservationResponse]:
    reservations = use_case.execute(
        ListReservationsByBranchInput(
            branch_id=branch_id,
            date_from=date_from,
            date_to=date_to,
        )
    )
    return [_map_reservation(r) for r in reservations]


@router.get("/{reservation_id}", response_model=ReservationResponse)
def get_reservation(
    reservation_id: UUID,
    use_case: GetReservationUseCase = Depends(get_get_reservation_use_case),
    _: TokenPayload = Depends(get_current_token_payload),
) -> ReservationResponse:
    return _map_reservation(use_case.execute(reservation_id))


@router.post("/", response_model=ReservationResponse, status_code=status.HTTP_201_CREATED)
def create_reservation(
    body: CreateReservationRequest,
    use_case: CreateReservationUseCase = Depends(get_create_reservation_use_case),
    _: TokenPayload = Depends(get_current_token_payload),
) -> ReservationResponse:
    reservation = use_case.execute(
        CreateReservationInput(
            branch_id=body.branch_id,
            created_by_user_id=body.created_by_user_id,
            guest_name=body.guest_name,
            party_size=body.party_size,
            scheduled_at=body.scheduled_at,
            duration_minutes=body.duration_minutes,
            table_ids=body.table_ids,
            guest_phone=body.guest_phone,
            notes=body.notes,
        )
    )
    return _map_reservation(reservation)


@router.patch("/{reservation_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_reservation(
    reservation_id: UUID,
    body: UpdateReservationRequest,
    use_case: UpdateReservationUseCase = Depends(get_update_reservation_use_case),
    _: TokenPayload = Depends(get_current_token_payload),
) -> None:
    use_case.execute(
        UpdateReservationInput(
            reservation_id=reservation_id,
            guest_name=body.guest_name,
            guest_phone=body.guest_phone,
            party_size=body.party_size,
            scheduled_at=body.scheduled_at,
            duration_minutes=body.duration_minutes,
            notes=body.notes,
            table_ids=body.table_ids,
        )
    )


@router.post("/{reservation_id}/seat", response_model=OrderResponse)
def seat_reservation(
    reservation_id: UUID,
    use_case: SeatReservationUseCase = Depends(get_seat_reservation_use_case),
    _: TokenPayload = Depends(get_current_token_payload),
) -> OrderResponse:
    from app.presentation.routers.orders import _map_order
    order = use_case.execute(SeatReservationInput(reservation_id=reservation_id))
    return _map_order(order)


@router.post("/{reservation_id}/cancel", status_code=status.HTTP_204_NO_CONTENT)
def cancel_reservation(
    reservation_id: UUID,
    body: CancelReservationRequest,
    use_case: CancelReservationUseCase = Depends(get_cancel_reservation_use_case),
    _: TokenPayload = Depends(get_current_token_payload),
) -> None:
    use_case.execute(
        CancelReservationInput(reservation_id=reservation_id, reason=body.reason)
    )


@router.post("/{reservation_id}/no-show", status_code=status.HTTP_204_NO_CONTENT)
def mark_no_show(
    reservation_id: UUID,
    use_case: MarkNoShowUseCase = Depends(get_mark_no_show_use_case),
    _: TokenPayload = Depends(get_current_token_payload),
) -> None:
    use_case.execute(MarkNoShowInput(reservation_id=reservation_id))
