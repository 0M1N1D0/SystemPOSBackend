from uuid import UUID

from fastapi import APIRouter, Depends

from app.application.use_cases.tax_rates.create_tax_rate import CreateTaxRateInput, CreateTaxRateUseCase
from app.application.use_cases.tax_rates.deactivate_tax_rate import DeactivateTaxRateUseCase
from app.application.use_cases.tax_rates.get_tax_rate import GetTaxRateUseCase
from app.application.use_cases.tax_rates.list_tax_rates import ListTaxRatesUseCase
from app.application.use_cases.tax_rates.set_default_tax_rate import SetDefaultTaxRateUseCase
from app.application.use_cases.tax_rates.update_tax_rate import UpdateTaxRateInput, UpdateTaxRateUseCase
from app.domain.services.i_token_service import TokenPayload
from app.presentation.dependencies import (
    get_create_tax_rate_use_case,
    get_deactivate_tax_rate_use_case,
    get_get_tax_rate_use_case,
    get_list_tax_rates_use_case,
    get_set_default_tax_rate_use_case,
    get_update_tax_rate_use_case,
    get_current_token_payload,
    require_admin,
)
from app.presentation.schemas.tax_rate import TaxRateCreate, TaxRateResponse, TaxRateUpdate

router = APIRouter()


def _to_response(t: object) -> TaxRateResponse:
    return TaxRateResponse(
        id=t.id,
        name=t.name,
        rate=t.rate,
        is_default=t.is_default,
        is_active=t.is_active,
    )


@router.get("/", response_model=list[TaxRateResponse])
def list_tax_rates(
    use_case: ListTaxRatesUseCase = Depends(get_list_tax_rates_use_case),
    _: TokenPayload = Depends(get_current_token_payload),
) -> list[TaxRateResponse]:
    return [_to_response(t) for t in use_case.execute()]


@router.get("/{tax_rate_id}", response_model=TaxRateResponse)
def get_tax_rate(
    tax_rate_id: UUID,
    use_case: GetTaxRateUseCase = Depends(get_get_tax_rate_use_case),
    _: TokenPayload = Depends(get_current_token_payload),
) -> TaxRateResponse:
    return _to_response(use_case.execute(tax_rate_id))


@router.post("/", response_model=TaxRateResponse, status_code=201)
def create_tax_rate(
    body: TaxRateCreate,
    use_case: CreateTaxRateUseCase = Depends(get_create_tax_rate_use_case),
    _: TokenPayload = Depends(require_admin),
) -> TaxRateResponse:
    t = use_case.execute(
        CreateTaxRateInput(name=body.name, rate=body.rate, is_default=body.is_default)
    )
    return _to_response(t)


@router.patch("/{tax_rate_id}", response_model=TaxRateResponse)
def update_tax_rate(
    tax_rate_id: UUID,
    body: TaxRateUpdate,
    use_case: UpdateTaxRateUseCase = Depends(get_update_tax_rate_use_case),
    _: TokenPayload = Depends(require_admin),
) -> TaxRateResponse:
    t = use_case.execute(
        UpdateTaxRateInput(tax_rate_id=tax_rate_id, name=body.name, rate=body.rate)
    )
    return _to_response(t)


@router.delete("/{tax_rate_id}", status_code=204)
def deactivate_tax_rate(
    tax_rate_id: UUID,
    use_case: DeactivateTaxRateUseCase = Depends(get_deactivate_tax_rate_use_case),
    _: TokenPayload = Depends(require_admin),
) -> None:
    use_case.execute(tax_rate_id)


@router.post("/{tax_rate_id}/set-default", response_model=TaxRateResponse)
def set_default_tax_rate(
    tax_rate_id: UUID,
    use_case: SetDefaultTaxRateUseCase = Depends(get_set_default_tax_rate_use_case),
    _: TokenPayload = Depends(require_admin),
) -> TaxRateResponse:
    return _to_response(use_case.execute(tax_rate_id))
