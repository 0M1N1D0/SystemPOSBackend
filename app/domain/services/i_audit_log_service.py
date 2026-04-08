from abc import ABC, abstractmethod
from typing import Any, Optional
from uuid import UUID

from app.domain.enums import AuditAction


class IAuditLogService(ABC):
    @abstractmethod
    def log(
        self,
        user_id: UUID,
        action: AuditAction,
        details: Optional[dict[str, Any]] = None,
    ) -> None: ...
