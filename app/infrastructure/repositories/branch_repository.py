from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.entities.branch import Branch
from app.domain.repositories.i_branch_repository import IBranchRepository
from app.infrastructure.mappers import branch_mapper
from app.infrastructure.orm.branch import BranchORM


class SqlBranchRepository(IBranchRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, branch: Branch) -> Branch:
        orm = branch_mapper.to_orm(branch)
        self._session.add(orm)
        self._session.commit()
        self._session.refresh(orm)
        return branch_mapper.to_domain(orm)

    def find_by_id(self, branch_id: UUID) -> Optional[Branch]:
        orm = self._session.get(BranchORM, str(branch_id))
        return branch_mapper.to_domain(orm) if orm else None

    def find_all(self) -> list[Branch]:
        rows = self._session.query(BranchORM).all()
        return [branch_mapper.to_domain(r) for r in rows]

    def update(self, branch: Branch) -> Branch:
        orm = self._session.get(BranchORM, str(branch.id))
        orm.name = branch.name
        orm.address = branch.address
        orm.phone = branch.phone
        orm.is_active = branch.is_active
        self._session.commit()
        self._session.refresh(orm)
        return branch_mapper.to_domain(orm)
