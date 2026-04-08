from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

from app.domain.enums import RoleName


@dataclass
class TokenPayload:
    user_id: UUID
    role: RoleName


class ITokenService(ABC):
    @abstractmethod
    def create_access_token(
        self, user_id: UUID, role: RoleName, pin_based: bool = False
    ) -> str: ...

    @abstractmethod
    def decode_token(self, token: str) -> TokenPayload: ...
