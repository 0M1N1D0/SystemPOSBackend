from uuid import UUID

from pydantic import BaseModel, Field


class PinLoginRequest(BaseModel):
    user_id: UUID
    pin: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$")


class PasswordLoginRequest(BaseModel):
    email: str
    password: str = Field(min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
