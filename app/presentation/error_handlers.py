from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.domain.exceptions import (
    BusinessRuleViolationError,
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    InvalidTokenError,
    ModifierHasHistoryError,
    NotFoundError,
    UserInactiveError,
)


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(InvalidCredentialsError)
    async def invalid_credentials_handler(
        request: Request, exc: InvalidCredentialsError
    ) -> JSONResponse:
        return JSONResponse(status_code=401, content={"detail": str(exc)})

    @app.exception_handler(UserInactiveError)
    async def user_inactive_handler(
        request: Request, exc: UserInactiveError
    ) -> JSONResponse:
        return JSONResponse(status_code=403, content={"detail": str(exc)})

    @app.exception_handler(InvalidTokenError)
    async def invalid_token_handler(
        request: Request, exc: InvalidTokenError
    ) -> JSONResponse:
        return JSONResponse(status_code=401, content={"detail": str(exc)})

    @app.exception_handler(EmailAlreadyExistsError)
    async def email_exists_handler(
        request: Request, exc: EmailAlreadyExistsError
    ) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.exception_handler(BusinessRuleViolationError)
    async def business_rule_handler(
        request: Request, exc: BusinessRuleViolationError
    ) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    @app.exception_handler(ModifierHasHistoryError)
    async def modifier_has_history_handler(
        request: Request, exc: ModifierHasHistoryError
    ) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": str(exc)})
