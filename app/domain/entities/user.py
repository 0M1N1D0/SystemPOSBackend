from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

from app.domain.enums import RoleName


@dataclass
class User:
    id: UUID
    role_id: UUID
    role_name: RoleName
    given_name: str
    paternal_surname: str
    pin_hash: str
    is_active: bool
    created_at: datetime
    branch_id: Optional[UUID] = None
    maternal_surname: Optional[str] = None
    email: Optional[str] = None
    password_hash: Optional[str] = None
