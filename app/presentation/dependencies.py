from collections.abc import Generator
from uuid import UUID

from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.application.use_cases.auth.authenticate_with_password import (
    AuthenticateWithPasswordUseCase,
)
from app.application.use_cases.auth.authenticate_with_pin import (
    AuthenticateWithPinUseCase,
)
from app.application.use_cases.auth.logout import LogoutUseCase
from app.application.use_cases.branches.create_branch import CreateBranchUseCase
from app.application.use_cases.branches.deactivate_branch import DeactivateBranchUseCase
from app.application.use_cases.branches.get_branch import GetBranchUseCase
from app.application.use_cases.branches.list_branches import ListBranchesUseCase
from app.application.use_cases.branches.update_branch import UpdateBranchUseCase
from app.application.use_cases.users.change_password import ChangePasswordUseCase
from app.application.use_cases.users.change_pin import ChangePinUseCase
from app.application.use_cases.users.create_user import CreateUserUseCase
from app.application.use_cases.users.deactivate_user import DeactivateUserUseCase
from app.application.use_cases.users.get_user import GetUserUseCase
from app.application.use_cases.users.list_users import ListUsersUseCase
from app.application.use_cases.users.update_user import UpdateUserUseCase
from app.application.use_cases.catalog.create_category import CreateCategoryUseCase
from app.application.use_cases.catalog.update_category import UpdateCategoryUseCase
from app.application.use_cases.catalog.list_categories import ListCategoriesUseCase
from app.application.use_cases.catalog.get_category import GetCategoryUseCase
from app.application.use_cases.catalog.create_product import CreateProductUseCase
from app.application.use_cases.catalog.update_product import UpdateProductUseCase
from app.application.use_cases.catalog.update_product_price import UpdateProductPriceUseCase
from app.application.use_cases.catalog.toggle_product_availability import ToggleProductAvailabilityUseCase
from app.application.use_cases.catalog.list_products_by_category import ListProductsByCategoryUseCase
from app.application.use_cases.catalog.get_product import GetProductUseCase
from app.application.use_cases.catalog.create_modifier import CreateModifierUseCase
from app.application.use_cases.catalog.update_modifier import UpdateModifierUseCase
from app.application.use_cases.catalog.delete_modifier import DeleteModifierUseCase
from app.application.use_cases.catalog.list_modifiers_by_product import ListModifiersByProductUseCase
from app.application.use_cases.tax_rates.create_tax_rate import CreateTaxRateUseCase
from app.application.use_cases.tax_rates.update_tax_rate import UpdateTaxRateUseCase
from app.application.use_cases.tax_rates.deactivate_tax_rate import DeactivateTaxRateUseCase
from app.application.use_cases.tax_rates.set_default_tax_rate import SetDefaultTaxRateUseCase
from app.application.use_cases.tax_rates.list_tax_rates import ListTaxRatesUseCase
from app.application.use_cases.tax_rates.get_tax_rate import GetTaxRateUseCase
from app.application.use_cases.tables.create_table import CreateTableUseCase
from app.application.use_cases.tables.update_table import UpdateTableUseCase
from app.application.use_cases.tables.get_table import GetTableUseCase
from app.application.use_cases.tables.list_tables_by_branch import ListTablesByBranchUseCase
from app.application.use_cases.orders.create_order import CreateOrderUseCase
from app.application.use_cases.orders.add_order_item import AddOrderItemUseCase
from app.application.use_cases.orders.remove_order_item import RemoveOrderItemUseCase
from app.application.use_cases.orders.update_order_item import UpdateOrderItemUseCase
from app.application.use_cases.orders.update_order_item_status import UpdateOrderItemStatusUseCase
from app.application.use_cases.orders.pay_order import PayOrderUseCase
from app.application.use_cases.orders.cancel_order import CancelOrderUseCase
from app.application.use_cases.orders.apply_discount import ApplyDiscountUseCase
from app.application.use_cases.orders.assign_table import AssignTableUseCase
from app.application.use_cases.orders.release_table import ReleaseTableUseCase
from app.application.use_cases.orders.get_order import GetOrderUseCase
from app.application.use_cases.orders.list_open_orders import ListOpenOrdersUseCase
from app.config import settings
from app.domain.enums import RoleName
from app.domain.services.i_token_service import TokenPayload
from app.infrastructure.database import get_session
from app.infrastructure.repositories.category_repository import SqlCategoryRepository
from app.infrastructure.repositories.product_repository import SqlProductRepository
from app.infrastructure.repositories.modifier_repository import SqlModifierRepository
from app.infrastructure.repositories.audit_log_repository import SqlAuditLogRepository
from app.infrastructure.repositories.branch_repository import SqlBranchRepository
from app.infrastructure.repositories.role_repository import SqlRoleRepository
from app.infrastructure.repositories.user_repository import SqlUserRepository
from app.infrastructure.repositories.tax_rate_repository import SqlTaxRateRepository
from app.infrastructure.repositories.restaurant_table_repository import SqlRestaurantTableRepository
from app.infrastructure.repositories.order_repository import SqlOrderRepository
from app.infrastructure.services.audit_log_service import AuditLogService
from app.infrastructure.services.bcrypt_hasher import BcryptHasher
from app.infrastructure.services.jwt_token_service import JwtTokenService

_security = HTTPBearer()
_hasher = BcryptHasher()


def get_token_service() -> JwtTokenService:
    return JwtTokenService(
        secret_key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
        pin_expire_minutes=settings.JWT_PIN_TOKEN_EXPIRE_MINUTES,
        password_expire_minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
    )


def get_current_token_payload(
    credentials: HTTPAuthorizationCredentials = Security(_security),
    token_service: JwtTokenService = Depends(get_token_service),
) -> TokenPayload:
    return token_service.decode_token(credentials.credentials)


def require_admin(
    payload: TokenPayload = Depends(get_current_token_payload),
) -> TokenPayload:
    if payload.role != RoleName.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    return payload


def require_manager_or_above(
    payload: TokenPayload = Depends(get_current_token_payload),
) -> TokenPayload:
    if payload.role not in (RoleName.ADMIN, RoleName.MANAGER):
        raise HTTPException(status_code=403, detail="Manager or Admin access required")
    return payload


# --- Infrastructure factories ---

def _audit_service(session: Session) -> AuditLogService:
    return AuditLogService(SqlAuditLogRepository(session))


# --- Auth use cases ---

def get_pin_auth_use_case(
    session: Session = Depends(get_session),
    token_service: JwtTokenService = Depends(get_token_service),
) -> AuthenticateWithPinUseCase:
    return AuthenticateWithPinUseCase(
        user_repo=SqlUserRepository(session),
        hasher=_hasher,
        token_service=token_service,
        audit_service=_audit_service(session),
    )


def get_password_auth_use_case(
    session: Session = Depends(get_session),
    token_service: JwtTokenService = Depends(get_token_service),
) -> AuthenticateWithPasswordUseCase:
    return AuthenticateWithPasswordUseCase(
        user_repo=SqlUserRepository(session),
        hasher=_hasher,
        token_service=token_service,
        audit_service=_audit_service(session),
    )


def get_logout_use_case(
    session: Session = Depends(get_session),
) -> LogoutUseCase:
    return LogoutUseCase(audit_service=_audit_service(session))


# --- Branch use cases ---

def get_create_branch_use_case(
    session: Session = Depends(get_session),
) -> CreateBranchUseCase:
    return CreateBranchUseCase(SqlBranchRepository(session))


def get_update_branch_use_case(
    session: Session = Depends(get_session),
) -> UpdateBranchUseCase:
    return UpdateBranchUseCase(SqlBranchRepository(session))


def get_deactivate_branch_use_case(
    session: Session = Depends(get_session),
) -> DeactivateBranchUseCase:
    return DeactivateBranchUseCase(SqlBranchRepository(session))


def get_branch_use_case(
    session: Session = Depends(get_session),
) -> GetBranchUseCase:
    return GetBranchUseCase(SqlBranchRepository(session))


def get_list_branches_use_case(
    session: Session = Depends(get_session),
) -> ListBranchesUseCase:
    return ListBranchesUseCase(SqlBranchRepository(session))


# --- User use cases ---

def get_create_user_use_case(
    session: Session = Depends(get_session),
    payload: TokenPayload = Depends(get_current_token_payload),
) -> CreateUserUseCase:
    return CreateUserUseCase(
        user_repo=SqlUserRepository(session),
        role_repo=SqlRoleRepository(session),
        branch_repo=SqlBranchRepository(session),
        hasher=_hasher,
        audit_service=_audit_service(session),
        actor_user_id=payload.user_id,
    )


def get_update_user_use_case(
    session: Session = Depends(get_session),
    payload: TokenPayload = Depends(get_current_token_payload),
) -> UpdateUserUseCase:
    return UpdateUserUseCase(
        user_repo=SqlUserRepository(session),
        branch_repo=SqlBranchRepository(session),
        audit_service=_audit_service(session),
        actor_user_id=payload.user_id,
    )


def get_deactivate_user_use_case(
    session: Session = Depends(get_session),
    payload: TokenPayload = Depends(get_current_token_payload),
) -> DeactivateUserUseCase:
    return DeactivateUserUseCase(
        user_repo=SqlUserRepository(session),
        audit_service=_audit_service(session),
        actor_user_id=payload.user_id,
    )


def get_change_pin_use_case(
    session: Session = Depends(get_session),
) -> ChangePinUseCase:
    return ChangePinUseCase(
        user_repo=SqlUserRepository(session),
        hasher=_hasher,
        audit_service=_audit_service(session),
    )


def get_change_password_use_case(
    session: Session = Depends(get_session),
) -> ChangePasswordUseCase:
    return ChangePasswordUseCase(
        user_repo=SqlUserRepository(session),
        hasher=_hasher,
        audit_service=_audit_service(session),
    )


def get_get_user_use_case(
    session: Session = Depends(get_session),
) -> GetUserUseCase:
    return GetUserUseCase(SqlUserRepository(session))


def get_list_users_use_case(
    session: Session = Depends(get_session),
) -> ListUsersUseCase:
    return ListUsersUseCase(SqlUserRepository(session))


# --- Tax Rate use cases ---

def get_create_tax_rate_use_case(
    session: Session = Depends(get_session),
    payload: TokenPayload = Depends(get_current_token_payload),
) -> CreateTaxRateUseCase:
    return CreateTaxRateUseCase(
        tax_rate_repo=SqlTaxRateRepository(session),
        audit_service=_audit_service(session),
        actor_user_id=payload.user_id,
    )


def get_update_tax_rate_use_case(
    session: Session = Depends(get_session),
    payload: TokenPayload = Depends(get_current_token_payload),
) -> UpdateTaxRateUseCase:
    return UpdateTaxRateUseCase(
        tax_rate_repo=SqlTaxRateRepository(session),
        audit_service=_audit_service(session),
        actor_user_id=payload.user_id,
    )


def get_deactivate_tax_rate_use_case(
    session: Session = Depends(get_session),
    payload: TokenPayload = Depends(get_current_token_payload),
) -> DeactivateTaxRateUseCase:
    return DeactivateTaxRateUseCase(
        tax_rate_repo=SqlTaxRateRepository(session),
        audit_service=_audit_service(session),
        actor_user_id=payload.user_id,
    )


def get_set_default_tax_rate_use_case(
    session: Session = Depends(get_session),
    payload: TokenPayload = Depends(get_current_token_payload),
) -> SetDefaultTaxRateUseCase:
    return SetDefaultTaxRateUseCase(
        tax_rate_repo=SqlTaxRateRepository(session),
        audit_service=_audit_service(session),
        actor_user_id=payload.user_id,
    )


def get_list_tax_rates_use_case(
    session: Session = Depends(get_session),
) -> ListTaxRatesUseCase:
    return ListTaxRatesUseCase(SqlTaxRateRepository(session))


def get_get_tax_rate_use_case(
    session: Session = Depends(get_session),
) -> GetTaxRateUseCase:
    return GetTaxRateUseCase(SqlTaxRateRepository(session))


# --- Catalog use cases ---

def get_create_category_use_case(
    session: Session = Depends(get_session),
    payload: TokenPayload = Depends(get_current_token_payload),
) -> CreateCategoryUseCase:
    return CreateCategoryUseCase(
        category_repo=SqlCategoryRepository(session),
        audit_service=_audit_service(session),
        actor_user_id=payload.user_id,
    )


def get_update_category_use_case(
    session: Session = Depends(get_session),
    payload: TokenPayload = Depends(get_current_token_payload),
) -> UpdateCategoryUseCase:
    return UpdateCategoryUseCase(
        category_repo=SqlCategoryRepository(session),
        audit_service=_audit_service(session),
        actor_user_id=payload.user_id,
    )


def get_list_categories_use_case(
    session: Session = Depends(get_session),
) -> ListCategoriesUseCase:
    return ListCategoriesUseCase(SqlCategoryRepository(session))


def get_get_category_use_case(
    session: Session = Depends(get_session),
) -> GetCategoryUseCase:
    return GetCategoryUseCase(SqlCategoryRepository(session))


def get_create_product_use_case(
    session: Session = Depends(get_session),
    payload: TokenPayload = Depends(get_current_token_payload),
) -> CreateProductUseCase:
    return CreateProductUseCase(
        product_repo=SqlProductRepository(session),
        category_repo=SqlCategoryRepository(session),
        tax_rate_repo=SqlTaxRateRepository(session),
        audit_service=_audit_service(session),
        actor_user_id=payload.user_id,
    )


def get_update_product_use_case(
    session: Session = Depends(get_session),
    payload: TokenPayload = Depends(get_current_token_payload),
) -> UpdateProductUseCase:
    return UpdateProductUseCase(
        product_repo=SqlProductRepository(session),
        category_repo=SqlCategoryRepository(session),
        tax_rate_repo=SqlTaxRateRepository(session),
        audit_service=_audit_service(session),
        actor_user_id=payload.user_id,
    )


def get_update_product_price_use_case(
    session: Session = Depends(get_session),
    payload: TokenPayload = Depends(get_current_token_payload),
) -> UpdateProductPriceUseCase:
    return UpdateProductPriceUseCase(
        product_repo=SqlProductRepository(session),
        audit_service=_audit_service(session),
        actor_user_id=payload.user_id,
    )


def get_toggle_product_availability_use_case(
    session: Session = Depends(get_session),
    payload: TokenPayload = Depends(get_current_token_payload),
) -> ToggleProductAvailabilityUseCase:
    return ToggleProductAvailabilityUseCase(
        product_repo=SqlProductRepository(session),
        audit_service=_audit_service(session),
        actor_user_id=payload.user_id,
    )


def get_list_products_by_category_use_case(
    session: Session = Depends(get_session),
) -> ListProductsByCategoryUseCase:
    return ListProductsByCategoryUseCase(
        product_repo=SqlProductRepository(session),
        category_repo=SqlCategoryRepository(session),
    )


def get_get_product_use_case(
    session: Session = Depends(get_session),
) -> GetProductUseCase:
    return GetProductUseCase(SqlProductRepository(session))


def get_create_modifier_use_case(
    session: Session = Depends(get_session),
    payload: TokenPayload = Depends(get_current_token_payload),
) -> CreateModifierUseCase:
    return CreateModifierUseCase(
        modifier_repo=SqlModifierRepository(session),
        product_repo=SqlProductRepository(session),
        audit_service=_audit_service(session),
        actor_user_id=payload.user_id,
    )


def get_update_modifier_use_case(
    session: Session = Depends(get_session),
    payload: TokenPayload = Depends(get_current_token_payload),
) -> UpdateModifierUseCase:
    return UpdateModifierUseCase(
        modifier_repo=SqlModifierRepository(session),
        audit_service=_audit_service(session),
        actor_user_id=payload.user_id,
    )


def get_delete_modifier_use_case(
    session: Session = Depends(get_session),
    payload: TokenPayload = Depends(get_current_token_payload),
) -> DeleteModifierUseCase:
    return DeleteModifierUseCase(
        modifier_repo=SqlModifierRepository(session),
        audit_service=_audit_service(session),
        actor_user_id=payload.user_id,
    )


def get_list_modifiers_by_product_use_case(
    session: Session = Depends(get_session),
) -> ListModifiersByProductUseCase:
    return ListModifiersByProductUseCase(
        modifier_repo=SqlModifierRepository(session),
        product_repo=SqlProductRepository(session),
    )


# --- Table use cases ---

def get_create_table_use_case(
    session: Session = Depends(get_session),
) -> CreateTableUseCase:
    return CreateTableUseCase(
        table_repo=SqlRestaurantTableRepository(session),
        branch_repo=SqlBranchRepository(session),
    )


def get_update_table_use_case(
    session: Session = Depends(get_session),
) -> UpdateTableUseCase:
    return UpdateTableUseCase(SqlRestaurantTableRepository(session))


def get_get_table_use_case(
    session: Session = Depends(get_session),
) -> GetTableUseCase:
    return GetTableUseCase(SqlRestaurantTableRepository(session))


def get_list_tables_by_branch_use_case(
    session: Session = Depends(get_session),
) -> ListTablesByBranchUseCase:
    return ListTablesByBranchUseCase(
        table_repo=SqlRestaurantTableRepository(session),
        branch_repo=SqlBranchRepository(session),
    )


# --- Order use cases ---

def get_create_order_use_case(
    session: Session = Depends(get_session),
    payload: TokenPayload = Depends(get_current_token_payload),
) -> CreateOrderUseCase:
    return CreateOrderUseCase(
        order_repo=SqlOrderRepository(session),
        table_repo=SqlRestaurantTableRepository(session),
        user_repo=SqlUserRepository(session),
        audit_service=_audit_service(session),
        actor_user_id=payload.user_id,
    )


def get_add_order_item_use_case(
    session: Session = Depends(get_session),
    payload: TokenPayload = Depends(get_current_token_payload),
) -> AddOrderItemUseCase:
    return AddOrderItemUseCase(
        order_repo=SqlOrderRepository(session),
        product_repo=SqlProductRepository(session),
        modifier_repo=SqlModifierRepository(session),
        tax_rate_repo=SqlTaxRateRepository(session),
        audit_service=_audit_service(session),
        actor_user_id=payload.user_id,
    )


def get_remove_order_item_use_case(
    session: Session = Depends(get_session),
    payload: TokenPayload = Depends(get_current_token_payload),
) -> RemoveOrderItemUseCase:
    return RemoveOrderItemUseCase(
        order_repo=SqlOrderRepository(session),
        audit_service=_audit_service(session),
        actor_user_id=payload.user_id,
    )


def get_update_order_item_use_case(
    session: Session = Depends(get_session),
    payload: TokenPayload = Depends(get_current_token_payload),
) -> UpdateOrderItemUseCase:
    return UpdateOrderItemUseCase(
        order_repo=SqlOrderRepository(session),
        audit_service=_audit_service(session),
        actor_user_id=payload.user_id,
    )


def get_update_order_item_status_use_case(
    session: Session = Depends(get_session),
) -> UpdateOrderItemStatusUseCase:
    return UpdateOrderItemStatusUseCase(SqlOrderRepository(session))


def get_pay_order_use_case(
    session: Session = Depends(get_session),
    payload: TokenPayload = Depends(get_current_token_payload),
) -> PayOrderUseCase:
    return PayOrderUseCase(
        order_repo=SqlOrderRepository(session),
        table_repo=SqlRestaurantTableRepository(session),
        audit_service=_audit_service(session),
        actor_user_id=payload.user_id,
    )


def get_cancel_order_use_case(
    session: Session = Depends(get_session),
    payload: TokenPayload = Depends(get_current_token_payload),
) -> CancelOrderUseCase:
    return CancelOrderUseCase(
        order_repo=SqlOrderRepository(session),
        table_repo=SqlRestaurantTableRepository(session),
        audit_service=_audit_service(session),
        actor_user_id=payload.user_id,
    )


def get_apply_discount_use_case(
    session: Session = Depends(get_session),
    payload: TokenPayload = Depends(get_current_token_payload),
) -> ApplyDiscountUseCase:
    return ApplyDiscountUseCase(
        order_repo=SqlOrderRepository(session),
        audit_service=_audit_service(session),
        actor_user_id=payload.user_id,
        actor_role=payload.role,
    )


def get_assign_table_use_case(
    session: Session = Depends(get_session),
    payload: TokenPayload = Depends(get_current_token_payload),
) -> AssignTableUseCase:
    return AssignTableUseCase(
        order_repo=SqlOrderRepository(session),
        table_repo=SqlRestaurantTableRepository(session),
        audit_service=_audit_service(session),
        actor_user_id=payload.user_id,
    )


def get_release_table_use_case(
    session: Session = Depends(get_session),
    payload: TokenPayload = Depends(get_current_token_payload),
) -> ReleaseTableUseCase:
    return ReleaseTableUseCase(
        order_repo=SqlOrderRepository(session),
        table_repo=SqlRestaurantTableRepository(session),
        audit_service=_audit_service(session),
        actor_user_id=payload.user_id,
    )


def get_get_order_use_case(
    session: Session = Depends(get_session),
) -> GetOrderUseCase:
    return GetOrderUseCase(SqlOrderRepository(session))


def get_list_open_orders_use_case(
    session: Session = Depends(get_session),
) -> ListOpenOrdersUseCase:
    return ListOpenOrdersUseCase(SqlOrderRepository(session))
