import uuid

from app.domain.entities.audit_log import AuditLog
from app.domain.enums import AuditAction
from app.infrastructure.orm.audit_log import AuditLogORM


def to_domain(orm: AuditLogORM) -> AuditLog:
    return AuditLog(
        id=uuid.UUID(orm.id),
        user_id=uuid.UUID(orm.user_id),
        action=AuditAction(orm.action),
        timestamp=orm.timestamp,
        details=orm.details,
    )


def to_orm(entity: AuditLog) -> AuditLogORM:
    return AuditLogORM(
        id=str(entity.id),
        user_id=str(entity.user_id),
        action=entity.action.value,
        details=entity.details,
        timestamp=entity.timestamp,
    )
