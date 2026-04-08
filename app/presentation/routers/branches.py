from uuid import UUID

from fastapi import APIRouter, Depends

from app.application.use_cases.branches.create_branch import CreateBranchInput, CreateBranchUseCase
from app.application.use_cases.branches.deactivate_branch import DeactivateBranchUseCase
from app.application.use_cases.branches.get_branch import GetBranchUseCase
from app.application.use_cases.branches.list_branches import ListBranchesUseCase
from app.application.use_cases.branches.update_branch import UpdateBranchInput, UpdateBranchUseCase
from app.domain.services.i_token_service import TokenPayload
from app.presentation.dependencies import (
    get_branch_use_case,
    get_create_branch_use_case,
    get_deactivate_branch_use_case,
    get_list_branches_use_case,
    get_update_branch_use_case,
    require_admin,
    get_current_token_payload,
)
from app.presentation.schemas.branch import BranchCreate, BranchResponse, BranchUpdate

router = APIRouter()


@router.get("/", response_model=list[BranchResponse])
def list_branches(
    use_case: ListBranchesUseCase = Depends(get_list_branches_use_case),
    _: TokenPayload = Depends(get_current_token_payload),
) -> list[BranchResponse]:
    branches = use_case.execute()
    return [
        BranchResponse(
            id=b.id,
            name=b.name,
            address=b.address,
            phone=b.phone,
            is_active=b.is_active,
        )
        for b in branches
    ]


@router.get("/{branch_id}", response_model=BranchResponse)
def get_branch(
    branch_id: UUID,
    use_case: GetBranchUseCase = Depends(get_branch_use_case),
    _: TokenPayload = Depends(get_current_token_payload),
) -> BranchResponse:
    b = use_case.execute(branch_id)
    return BranchResponse(id=b.id, name=b.name, address=b.address, phone=b.phone, is_active=b.is_active)


@router.post("/", response_model=BranchResponse, status_code=201)
def create_branch(
    body: BranchCreate,
    use_case: CreateBranchUseCase = Depends(get_create_branch_use_case),
    _: TokenPayload = Depends(require_admin),
) -> BranchResponse:
    b = use_case.execute(CreateBranchInput(name=body.name, address=body.address, phone=body.phone))
    return BranchResponse(id=b.id, name=b.name, address=b.address, phone=b.phone, is_active=b.is_active)


@router.patch("/{branch_id}", response_model=BranchResponse)
def update_branch(
    branch_id: UUID,
    body: BranchUpdate,
    use_case: UpdateBranchUseCase = Depends(get_update_branch_use_case),
    _: TokenPayload = Depends(require_admin),
) -> BranchResponse:
    b = use_case.execute(
        UpdateBranchInput(
            branch_id=branch_id,
            name=body.name,
            address=body.address,
            phone=body.phone,
        )
    )
    return BranchResponse(id=b.id, name=b.name, address=b.address, phone=b.phone, is_active=b.is_active)


@router.delete("/{branch_id}", status_code=204)
def deactivate_branch(
    branch_id: UUID,
    use_case: DeactivateBranchUseCase = Depends(get_deactivate_branch_use_case),
    _: TokenPayload = Depends(require_admin),
) -> None:
    use_case.execute(branch_id)
