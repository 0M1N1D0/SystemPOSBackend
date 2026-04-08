from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass
class Branch:
    id: UUID
    name: str
    is_active: bool
    address: Optional[str] = None
    phone: Optional[str] = None
