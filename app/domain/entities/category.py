from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass
class Category:
    id: UUID
    name: str
    description: Optional[str]
    sort_order: Optional[int]
