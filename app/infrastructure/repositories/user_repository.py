from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.entities.user import User
from app.domain.repositories.i_user_repository import IUserRepository
from app.infrastructure.mappers import user_mapper
from app.infrastructure.orm.user import UserORM


class SqlUserRepository(IUserRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, user: User) -> User:
        orm = user_mapper.to_orm(user)
        self._session.add(orm)
        self._session.commit()
        self._session.refresh(orm)
        # reload with joined role
        reloaded = self._session.get(UserORM, orm.id)
        return user_mapper.to_domain(reloaded)

    def find_by_id(self, user_id: UUID) -> Optional[User]:
        orm = self._session.get(UserORM, str(user_id))
        return user_mapper.to_domain(orm) if orm else None

    def find_by_email(self, email: str) -> Optional[User]:
        orm = self._session.query(UserORM).filter_by(email=email).first()
        return user_mapper.to_domain(orm) if orm else None

    def find_all(self) -> list[User]:
        rows = self._session.query(UserORM).all()
        return [user_mapper.to_domain(r) for r in rows]

    def find_all_by_branch(self, branch_id: UUID) -> list[User]:
        rows = self._session.query(UserORM).filter_by(branch_id=str(branch_id)).all()
        return [user_mapper.to_domain(r) for r in rows]

    def update(self, user: User) -> User:
        orm = self._session.get(UserORM, str(user.id))
        orm.given_name = user.given_name
        orm.paternal_surname = user.paternal_surname
        orm.maternal_surname = user.maternal_surname
        orm.email = user.email
        orm.password_hash = user.password_hash
        orm.pin_hash = user.pin_hash
        orm.is_active = user.is_active
        orm.branch_id = str(user.branch_id) if user.branch_id else None
        self._session.commit()
        self._session.refresh(orm)
        return user_mapper.to_domain(orm)
