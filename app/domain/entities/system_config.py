from dataclasses import dataclass
from typing import Optional


@dataclass
class SystemConfig:
    key: str
    value: str
    description: Optional[str] = None
