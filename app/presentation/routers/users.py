from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.application.use_cases.users.change_password import ChangePasswordInput, ChangePasswordUseCase
from app.application.use_cases.users.change_pin import ChangePinInput, ChangePinUseCase
from app.application.use_cases.users.create_user import CreateUserInput, CreateUserUseCase
from app.application.use_cases.users.deactivate_user import DeactivateUserUseCase
from app.application.use_cases.users.get_user import GetUserUseCase
from app.application.use_cases.users.list_users import ListUsersUseCase
from app.application.use_cases.users.update_user import UpdateUserInput, UpdateUserUseCase
from app.domain.services.i_token_service import TokenPayload
from app.presentation.dependencies import (
    get_change_password_use_case,
    get_change_pin_use_case,
    get_create_user_use_case,
    get_current_token_payload,
    get_deactivate_user_use_case,
    get_get_user_use_case,
    get_list_users_use_case,
    get_update_user_use_case,
    require_admin,
)
from app.presentation.schemas.user import (
    ChangePinRequest,
    ChangePasswordRequest,
    UserCreate,
    UserResponse,
    UserUpdate,
)

router = APIRouter()


def _to_response(user) -> UserResponse:
    return UserResponse(
        id=user.id,
        role_id=user.role_id,
        role_name=user.role_name.value,
        branch_id=user.branch_id,
        given_name=user.given_name,
        paternal_surname=user.paternal_surname,
        maternal_surname=user.maternal_surname,
        email=user.email,
        is_active=user.is_active,
        created_at=user.created_at,
    )


@router.get("/", response_model=list[UserResponse])
def list_users(
    branch_id: Optional[UUID] = Query(None),
    use_case: ListUsersUseCase = Depends(get_list_users_use_case),
    _: TokenPayload = Depends(get_current_token_payload),
) -> list[UserResponse]:
    users = use_case.execute(branch_id=branch_id)
    return [_to_response(u) for u in users]


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: UUID,
    use_case: GetUserUseCase = Depends(get_get_user_use_case),
    _: TokenPayload = Depends(get_current_token_payload),
) -> UserResponse:
    return _to_response(use_case.execute(user_id))


@router.post("/", response_model=UserResponse, status_code=201)
def create_user(
    body: UserCreate,
    use_case: CreateUserUseCase = Depends(get_create_user_use_case),
    _: TokenPayload = Depends(require_admin),
) -> UserResponse:
    user = use_case.execute(
        CreateUserInput(
            role_id=body.role_id,
            given_name=body.given_name,
            paternal_surname=body.paternal_surname,
            pin=body.pin,
            branch_id=body.branch_id,
            maternal_surname=body.maternal_surname,
            email=str(body.email) if body.email else None,
            password=body.password,
        )
    )
    return _to_response(user)


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: UUID,
    body: UserUpdate,
    use_case: UpdateUserUseCase = Depends(get_update_user_use_case),
    _: TokenPayload = Depends(require_admin),
) -> UserResponse:
    user = use_case.execute(
        UpdateUserInput(
            user_id=user_id,
            given_name=body.given_name,
            paternal_surname=body.paternal_surname,
            maternal_surname=body.maternal_surname,
            branch_id=body.branch_id,
        )
    )
    return _to_response(user)


@router.delete("/{user_id}", status_code=204)
def deactivate_user(
    user_id: UUID,
    use_case: DeactivateUserUseCase = Depends(get_deactivate_user_use_case),
    _: TokenPayload = Depends(require_admin),
) -> None:
    use_case.execute(user_id)


@router.post("/{user_id}/change-pin", status_code=204)
def change_pin(
    user_id: UUID,
    body: ChangePinRequest,
    use_case: ChangePinUseCase = Depends(get_change_pin_use_case),
    payload: TokenPayload = Depends(get_current_token_payload),
) -> None:
    # Users can only change their own PIN unless they are admin
    from app.domain.enums import RoleName
    if payload.user_id != user_id and payload.role != RoleName.ADMIN:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Cannot change another user's PIN")
    use_case.execute(ChangePinInput(user_id=user_id, current_pin=body.current_pin, new_pin=body.new_pin))


@router.post("/{user_id}/change-password", status_code=204)
def change_password(
    user_id: UUID,
    body: ChangePasswordRequest,
    use_case: ChangePasswordUseCase = Depends(get_change_password_use_case),
    payload: TokenPayload = Depends(get_current_token_payload),
) -> None:
    from app.domain.enums import RoleName
    if payload.user_id != user_id and payload.role != RoleName.ADMIN:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Cannot change another user's password")
    use_case.execute(
        ChangePasswordInput(
            user_id=user_id,
            current_password=body.current_password,
            new_password=body.new_password,
        )
    )
