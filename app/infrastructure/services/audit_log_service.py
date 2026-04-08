import uuid
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID

from app.domain.entities.audit_log import AuditLog
from app.domain.enums import AuditAction
from app.domain.repositories.i_audit_log_repository import IAuditLogRepository
from app.domain.services.i_audit_log_service import IAuditLogService


class AuditLogService(IAuditLogService):
    def __init__(self, audit_repo: IAuditLogRepository) -> None:
        self._repo = audit_repo

    def log(
        self,
        user_id: UUID,
        action: AuditAction,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        entry = AuditLog(
            id=uuid.uuid4(),
            user_id=user_id,
            action=action,
            timestamp=datetime.now(timezone.utc),
            details=details,
        )
        self._repo.save(entry)
