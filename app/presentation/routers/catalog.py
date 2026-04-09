from uuid import UUID

from fastapi import APIRouter, Depends

from app.application.use_cases.catalog.create_category import CreateCategoryInput, CreateCategoryUseCase
from app.application.use_cases.catalog.update_category import UpdateCategoryInput, UpdateCategoryUseCase
from app.application.use_cases.catalog.list_categories import ListCategoriesUseCase
from app.application.use_cases.catalog.get_category import GetCategoryUseCase
from app.application.use_cases.catalog.create_product import CreateProductInput, CreateProductUseCase
from app.application.use_cases.catalog.update_product import UpdateProductInput, UpdateProductUseCase
from app.application.use_cases.catalog.update_product_price import UpdateProductPriceInput, UpdateProductPriceUseCase
from app.application.use_cases.catalog.toggle_product_availability import ToggleProductAvailabilityUseCase
from app.application.use_cases.catalog.list_products_by_category import ListProductsByCategoryUseCase
from app.application.use_cases.catalog.get_product import GetProductUseCase
from app.application.use_cases.catalog.create_modifier import CreateModifierInput, CreateModifierUseCase
from app.application.use_cases.catalog.update_modifier import UpdateModifierInput, UpdateModifierUseCase
from app.application.use_cases.catalog.delete_modifier import DeleteModifierUseCase
from app.application.use_cases.catalog.list_modifiers_by_product import ListModifiersByProductUseCase
from app.domain.services.i_token_service import TokenPayload
from app.presentation.dependencies import (
    get_current_token_payload,
    require_admin,
    get_create_category_use_case,
    get_update_category_use_case,
    get_list_categories_use_case,
    get_get_category_use_case,
    get_create_product_use_case,
    get_update_product_use_case,
    get_update_product_price_use_case,
    get_toggle_product_availability_use_case,
    get_list_products_by_category_use_case,
    get_get_product_use_case,
    get_create_modifier_use_case,
    get_update_modifier_use_case,
    get_delete_modifier_use_case,
    get_list_modifiers_by_product_use_case,
)
from app.presentation.schemas.catalog import (
    CategoryCreate, CategoryUpdate, CategoryResponse,
    ProductCreate, ProductUpdate, ProductPriceUpdate, ProductResponse,
    ModifierCreate, ModifierUpdate, ModifierResponse,
)

router = APIRouter()


# ── Categories ──────────────────────────────────────────────────────────────

def _category_response(c: object) -> CategoryResponse:
    return CategoryResponse(
        id=c.id, name=c.name, description=c.description, sort_order=c.sort_order
    )


@router.get("/categories/", response_model=list[CategoryResponse])
def list_categories(
    use_case: ListCategoriesUseCase = Depends(get_list_categories_use_case),
    _: TokenPayload = Depends(get_current_token_payload),
) -> list[CategoryResponse]:
    return [_category_response(c) for c in use_case.execute()]


@router.get("/categories/{category_id}", response_model=CategoryResponse)
def get_category(
    category_id: UUID,
    use_case: GetCategoryUseCase = Depends(get_get_category_use_case),
    _: TokenPayload = Depends(get_current_token_payload),
) -> CategoryResponse:
    return _category_response(use_case.execute(category_id))


@router.post("/categories/", response_model=CategoryResponse, status_code=201)
def create_category(
    body: CategoryCreate,
    use_case: CreateCategoryUseCase = Depends(get_create_category_use_case),
    _: TokenPayload = Depends(require_admin),
) -> CategoryResponse:
    c = use_case.execute(
        CreateCategoryInput(
            name=body.name,
            description=body.description,
            sort_order=body.sort_order,
        )
    )
    return _category_response(c)


@router.patch("/categories/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: UUID,
    body: CategoryUpdate,
    use_case: UpdateCategoryUseCase = Depends(get_update_category_use_case),
    _: TokenPayload = Depends(require_admin),
) -> CategoryResponse:
    c = use_case.execute(
        UpdateCategoryInput(
            category_id=category_id,
            name=body.name,
            description=body.description,
            sort_order=body.sort_order,
        )
    )
    return _category_response(c)


# ── Products ─────────────────────────────────────────────────────────────────

def _product_response(p: object) -> ProductResponse:
    return ProductResponse(
        id=p.id,
        category_id=p.category_id,
        name=p.name,
        base_price=p.base_price,
        is_available=p.is_available,
        sort_order=p.sort_order,
        tax_rate_id=p.tax_rate_id,
    )


@router.get("/categories/{category_id}/products/", response_model=list[ProductResponse])
def list_products_by_category(
    category_id: UUID,
    use_case: ListProductsByCategoryUseCase = Depends(get_list_products_by_category_use_case),
    _: TokenPayload = Depends(get_current_token_payload),
) -> list[ProductResponse]:
    return [_product_response(p) for p in use_case.execute(category_id)]


@router.get("/products/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: UUID,
    use_case: GetProductUseCase = Depends(get_get_product_use_case),
    _: TokenPayload = Depends(get_current_token_payload),
) -> ProductResponse:
    return _product_response(use_case.execute(product_id))


@router.post("/products/", response_model=ProductResponse, status_code=201)
def create_product(
    body: ProductCreate,
    use_case: CreateProductUseCase = Depends(get_create_product_use_case),
    _: TokenPayload = Depends(require_admin),
) -> ProductResponse:
    p = use_case.execute(
        CreateProductInput(
            category_id=body.category_id,
            name=body.name,
            base_price=body.base_price,
            is_available=body.is_available,
            sort_order=body.sort_order,
            tax_rate_id=body.tax_rate_id,
        )
    )
    return _product_response(p)


@router.patch("/products/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: UUID,
    body: ProductUpdate,
    use_case: UpdateProductUseCase = Depends(get_update_product_use_case),
    _: TokenPayload = Depends(require_admin),
) -> ProductResponse:
    p = use_case.execute(
        UpdateProductInput(
            product_id=product_id,
            name=body.name,
            is_available=body.is_available,
            sort_order=body.sort_order,
            category_id=body.category_id,
            tax_rate_id=body.tax_rate_id,
        )
    )
    return _product_response(p)


@router.patch("/products/{product_id}/price", response_model=ProductResponse)
def update_product_price(
    product_id: UUID,
    body: ProductPriceUpdate,
    use_case: UpdateProductPriceUseCase = Depends(get_update_product_price_use_case),
    _: TokenPayload = Depends(require_admin),
) -> ProductResponse:
    return _product_response(
        use_case.execute(UpdateProductPriceInput(product_id=product_id, new_price=body.base_price))
    )


@router.post("/products/{product_id}/toggle-availability", response_model=ProductResponse)
def toggle_product_availability(
    product_id: UUID,
    use_case: ToggleProductAvailabilityUseCase = Depends(get_toggle_product_availability_use_case),
    _: TokenPayload = Depends(require_admin),
) -> ProductResponse:
    return _product_response(use_case.execute(product_id))


# ── Modifiers ────────────────────────────────────────────────────────────────

def _modifier_response(m: object) -> ModifierResponse:
    return ModifierResponse(
        id=m.id, product_id=m.product_id, name=m.name, extra_price=m.extra_price
    )


@router.get("/products/{product_id}/modifiers/", response_model=list[ModifierResponse])
def list_modifiers_by_product(
    product_id: UUID,
    use_case: ListModifiersByProductUseCase = Depends(get_list_modifiers_by_product_use_case),
    _: TokenPayload = Depends(get_current_token_payload),
) -> list[ModifierResponse]:
    return [_modifier_response(m) for m in use_case.execute(product_id)]


@router.post("/products/{product_id}/modifiers/", response_model=ModifierResponse, status_code=201)
def create_modifier(
    product_id: UUID,
    body: ModifierCreate,
    use_case: CreateModifierUseCase = Depends(get_create_modifier_use_case),
    _: TokenPayload = Depends(require_admin),
) -> ModifierResponse:
    m = use_case.execute(
        CreateModifierInput(
            product_id=product_id,
            name=body.name,
            extra_price=body.extra_price,
        )
    )
    return _modifier_response(m)


@router.patch("/modifiers/{modifier_id}", response_model=ModifierResponse)
def update_modifier(
    modifier_id: UUID,
    body: ModifierUpdate,
    use_case: UpdateModifierUseCase = Depends(get_update_modifier_use_case),
    _: TokenPayload = Depends(require_admin),
) -> ModifierResponse:
    m = use_case.execute(
        UpdateModifierInput(
            modifier_id=modifier_id,
            name=body.name,
            extra_price=body.extra_price,
        )
    )
    return _modifier_response(m)


@router.delete("/modifiers/{modifier_id}", status_code=204)
def delete_modifier(
    modifier_id: UUID,
    use_case: DeleteModifierUseCase = Depends(get_delete_modifier_use_case),
    _: TokenPayload = Depends(require_admin),
) -> None:
    use_case.execute(modifier_id)
