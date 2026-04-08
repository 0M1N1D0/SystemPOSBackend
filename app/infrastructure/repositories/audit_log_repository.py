from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.entities.audit_log import AuditLog
from app.domain.enums import AuditAction
from app.domain.repositories.i_audit_log_repository import IAuditLogRepository
from app.infrastructure.mappers import audit_log_mapper
from app.infrastructure.orm.audit_log import AuditLogORM


class SqlAuditLogRepository(IAuditLogRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, audit_log: AuditLog) -> None:
        orm = audit_log_mapper.to_orm(audit_log)
        self._session.add(orm)
        self._session.commit()

    def find_by_user(self, user_id: UUID) -> list[AuditLog]:
        rows = (
            self._session.query(AuditLogORM)
            .filter_by(user_id=str(user_id))
            .order_by(AuditLogORM.timestamp.desc())
            .all()
        )
        return [audit_log_mapper.to_domain(r) for r in rows]

    def find_by_action(self, action: AuditAction) -> list[AuditLog]:
        rows = (
            self._session.query(AuditLogORM)
            .filter_by(action=action.value)
            .order_by(AuditLogORM.timestamp.desc())
            .all()
        )
        return [audit_log_mapper.to_domain(r) for r in rows]
