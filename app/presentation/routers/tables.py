from uuid import UUID

from fastapi import APIRouter, Depends

from app.application.use_cases.tables.create_table import CreateTableInput, CreateTableUseCase
from app.application.use_cases.tables.get_table import GetTableUseCase
from app.application.use_cases.tables.list_tables_by_branch import ListTablesByBranchUseCase
from app.application.use_cases.tables.update_table import UpdateTableInput, UpdateTableUseCase
from app.domain.services.i_token_service import TokenPayload
from app.presentation.dependencies import (
    get_create_table_use_case,
    get_get_table_use_case,
    get_list_tables_by_branch_use_case,
    get_update_table_use_case,
    get_current_token_payload,
    require_admin,
)
from app.presentation.schemas.restaurant_table import TableCreate, TableResponse, TableUpdate

router = APIRouter()


@router.get("/", response_model=list[TableResponse])
def list_tables_by_branch(
    branch_id: UUID,
    use_case: ListTablesByBranchUseCase = Depends(get_list_tables_by_branch_use_case),
    _: TokenPayload = Depends(get_current_token_payload),
) -> list[TableResponse]:
    tables = use_case.execute(branch_id)
    return [
        TableResponse(
            id=t.id,
            branch_id=t.branch_id,
            identifier=t.identifier,
            capacity=t.capacity,
            status=t.status,
        )
        for t in tables
    ]


@router.get("/{table_id}", response_model=TableResponse)
def get_table(
    table_id: UUID,
    use_case: GetTableUseCase = Depends(get_get_table_use_case),
    _: TokenPayload = Depends(get_current_token_payload),
) -> TableResponse:
    t = use_case.execute(table_id)
    return TableResponse(
        id=t.id,
        branch_id=t.branch_id,
        identifier=t.identifier,
        capacity=t.capacity,
        status=t.status,
    )


@router.post("/", response_model=TableResponse, status_code=201)
def create_table(
    body: TableCreate,
    use_case: CreateTableUseCase = Depends(get_create_table_use_case),
    _: TokenPayload = Depends(require_admin),
) -> TableResponse:
    t = use_case.execute(
        CreateTableInput(
            branch_id=body.branch_id,
            identifier=body.identifier,
            capacity=body.capacity,
        )
    )
    return TableResponse(
        id=t.id,
        branch_id=t.branch_id,
        identifier=t.identifier,
        capacity=t.capacity,
        status=t.status,
    )


@router.patch("/{table_id}", response_model=TableResponse)
def update_table(
    table_id: UUID,
    body: TableUpdate,
    use_case: UpdateTableUseCase = Depends(get_update_table_use_case),
    _: TokenPayload = Depends(require_admin),
) -> TableResponse:
    t = use_case.execute(
        UpdateTableInput(
            table_id=table_id,
            identifier=body.identifier,
            capacity=body.capacity,
        )
    )
    return TableResponse(
        id=t.id,
        branch_id=t.branch_id,
        identifier=t.identifier,
        capacity=t.capacity,
        status=t.status,
    )
