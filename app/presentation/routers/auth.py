from fastapi import APIRouter, Depends

from app.application.use_cases.auth.authenticate_with_password import (
    AuthenticateWithPasswordUseCase,
    AuthenticateWithPasswordInput,
)
from app.application.use_cases.auth.authenticate_with_pin import (
    AuthenticateWithPinUseCase,
    AuthenticateWithPinInput,
)
from app.application.use_cases.auth.logout import LogoutUseCase
from app.domain.services.i_token_service import TokenPayload
from app.presentation.dependencies import (
    get_current_token_payload,
    get_logout_use_case,
    get_password_auth_use_case,
    get_pin_auth_use_case,
)
from app.presentation.schemas.auth import (
    PasswordLoginRequest,
    PinLoginRequest,
    TokenResponse,
)

router = APIRouter()


@router.post("/pin", response_model=TokenResponse)
def login_with_pin(
    body: PinLoginRequest,
    use_case: AuthenticateWithPinUseCase = Depends(get_pin_auth_use_case),
) -> TokenResponse:
    result = use_case.execute(AuthenticateWithPinInput(user_id=body.user_id, pin=body.pin))
    return TokenResponse(access_token=result.access_token, token_type=result.token_type)


@router.post("/password", response_model=TokenResponse)
def login_with_password(
    body: PasswordLoginRequest,
    use_case: AuthenticateWithPasswordUseCase = Depends(get_password_auth_use_case),
) -> TokenResponse:
    from app.application.use_cases.auth.authenticate_with_password import AuthenticateWithPasswordInput
    result = use_case.execute(
        AuthenticateWithPasswordInput(email=body.email, password=body.password)
    )
    return TokenResponse(access_token=result.access_token, token_type=result.token_type)


@router.post("/logout", status_code=204)
def logout(
    payload: TokenPayload = Depends(get_current_token_payload),
    use_case: LogoutUseCase = Depends(get_logout_use_case),
) -> None:
    use_case.execute(user_id=payload.user_id)
