from uuid import UUID

from app.domain.enums import AuditAction
from app.domain.services.i_audit_log_service import IAuditLogService


class LogoutUseCase:
    def __init__(self, audit_service: IAuditLogService) -> None:
        self._audit_service = audit_service

    def execute(self, user_id: UUID) -> None:
        self._audit_service.log(user_id=user_id, action=AuditAction.USER_LOGOUT)
