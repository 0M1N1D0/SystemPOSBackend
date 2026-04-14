from fastapi import APIRouter, Depends

from app.application.use_cases.config.get_config_value import GetConfigValueUseCase
from app.application.use_cases.config.list_config import ListConfigUseCase
from app.application.use_cases.config.set_config_value import SetConfigValueInput, SetConfigValueUseCase
from app.domain.services.i_token_service import TokenPayload
from app.presentation.dependencies import (
    get_get_config_value_use_case,
    get_list_config_use_case,
    get_set_config_value_use_case,
    require_admin,
)
from app.presentation.schemas.system_config import SystemConfigResponse, SystemConfigSet

router = APIRouter()


@router.get("/", response_model=list[SystemConfigResponse])
def list_config(
    use_case: ListConfigUseCase = Depends(get_list_config_use_case),
    _: TokenPayload = Depends(require_admin),
) -> list[SystemConfigResponse]:
    configs = use_case.execute()
    return [SystemConfigResponse(key=c.key, value=c.value, description=c.description) for c in configs]


@router.get("/{key}", response_model=SystemConfigResponse)
def get_config_value(
    key: str,
    use_case: GetConfigValueUseCase = Depends(get_get_config_value_use_case),
    _: TokenPayload = Depends(require_admin),
) -> SystemConfigResponse:
    c = use_case.execute(key)
    return SystemConfigResponse(key=c.key, value=c.value, description=c.description)


@router.put("/{key}", response_model=SystemConfigResponse)
def set_config_value(
    key: str,
    body: SystemConfigSet,
    use_case: SetConfigValueUseCase = Depends(get_set_config_value_use_case),
    _: TokenPayload = Depends(require_admin),
) -> SystemConfigResponse:
    c = use_case.execute(SetConfigValueInput(key=key, value=body.value, description=body.description))
    return SystemConfigResponse(key=c.key, value=c.value, description=c.description)
