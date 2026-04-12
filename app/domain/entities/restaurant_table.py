from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from app.domain.enums import TableStatus


@dataclass
class RestaurantTable:
    id: UUID
    branch_id: UUID
    identifier: str
    status: TableStatus
    capacity: Optional[int] = None
