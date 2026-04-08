from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from app.domain.enums import AuditAction


@dataclass
class AuditLog:
    id: UUID
    user_id: UUID
    action: AuditAction
    timestamp: datetime
    details: Optional[dict[str, Any]] = None
