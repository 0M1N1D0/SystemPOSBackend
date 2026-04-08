from dataclasses import dataclass
from uuid import UUID

from app.domain.enums import RoleName


@dataclass
class Role:
    id: UUID
    name: RoleName
