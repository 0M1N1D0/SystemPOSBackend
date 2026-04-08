from datetime import datetime, timedelta, timezone
from uuid import UUID

from jose import JWTError, jwt

from app.domain.enums import RoleName
from app.domain.exceptions import InvalidTokenError
from app.domain.services.i_token_service import ITokenService, TokenPayload


class JwtTokenService(ITokenService):
    def __init__(
        self,
        secret_key: str,
        algorithm: str,
        pin_expire_minutes: int,
        password_expire_minutes: int,
    ) -> None:
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._pin_expire_minutes = pin_expire_minutes
        self._password_expire_minutes = password_expire_minutes

    def create_access_token(
        self, user_id: UUID, role: RoleName, pin_based: bool = False
    ) -> str:
        expire_minutes = (
            self._pin_expire_minutes if pin_based else self._password_expire_minutes
        )
        payload = {
            "sub": str(user_id),
            "role": role.value,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=expire_minutes),
        }
        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

    def decode_token(self, token: str) -> TokenPayload:
        try:
            payload = jwt.decode(token, self._secret_key, algorithms=[self._algorithm])
            return TokenPayload(
                user_id=UUID(payload["sub"]),
                role=RoleName(payload["role"]),
            )
        except (JWTError, KeyError, ValueError) as exc:
            raise InvalidTokenError("Invalid or expired token") from exc
