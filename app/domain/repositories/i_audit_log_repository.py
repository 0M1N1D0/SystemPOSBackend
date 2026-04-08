from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.audit_log import AuditLog
from app.domain.enums import AuditAction


class IAuditLogRepository(ABC):
    @abstractmethod
    def save(self, audit_log: AuditLog) -> None: ...

    @abstractmethod
    def find_by_user(self, user_id: UUID) -> list[AuditLog]: ...

    @abstractmethod
    def find_by_action(self, action: AuditAction) -> list[AuditLog]: ...
