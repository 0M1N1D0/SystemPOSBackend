from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.application.use_cases.orders.add_order_item import AddOrderItemInput, AddOrderItemUseCase
from app.application.use_cases.orders.apply_discount import ApplyDiscountInput, ApplyDiscountUseCase
from app.application.use_cases.orders.assign_table import AssignTableInput, AssignTableUseCase
from app.application.use_cases.orders.cancel_order import CancelOrderInput, CancelOrderUseCase
from app.application.use_cases.orders.create_order import CreateOrderInput, CreateOrderUseCase
from app.application.use_cases.orders.get_order import GetOrderUseCase
from app.application.use_cases.orders.list_open_orders import ListOpenOrdersUseCase
from app.application.use_cases.orders.pay_order import PayOrderInput, PayOrderUseCase
from app.application.use_cases.orders.release_table import ReleaseTableInput, ReleaseTableUseCase
from app.application.use_cases.orders.remove_order_item import RemoveOrderItemInput, RemoveOrderItemUseCase
from app.application.use_cases.orders.update_order_item import UpdateOrderItemInput, UpdateOrderItemUseCase
from app.application.use_cases.orders.update_order_item_status import (
    UpdateOrderItemStatusInput,
    UpdateOrderItemStatusUseCase,
)
from app.domain.services.i_token_service import TokenPayload
from app.presentation.dependencies import (
    get_add_order_item_use_case,
    get_apply_discount_use_case,
    get_assign_table_use_case,
    get_cancel_order_use_case,
    get_create_order_use_case,
    get_get_order_use_case,
    get_list_open_orders_use_case,
    get_pay_order_use_case,
    get_release_table_use_case,
    get_remove_order_item_use_case,
    get_update_order_item_use_case,
    get_update_order_item_status_use_case,
    get_current_token_payload,
    require_manager_or_above,
)
from app.presentation.schemas.order import (
    AddOrderItemRequest,
    ApplyDiscountRequest,
    AssignTableRequest,
    CancelOrderRequest,
    CreateOrderRequest,
    OrderItemResponse,
    OrderResponse,
    PayOrderRequest,
    UpdateOrderItemRequest,
    UpdateOrderItemStatusRequest,
)

router = APIRouter()


def _map_order(order, use_case=None) -> OrderResponse:
    from app.presentation.schemas.order import OrderItemModifierResponse, OrderTableResponse

    return OrderResponse(
        id=order.id,
        user_id=order.user_id,
        subtotal=order.subtotal,
        taxes=order.taxes,
        tip=order.tip,
        discount=order.discount,
        total_amount=order.total_amount,
        status=order.status,
        payment_method=order.payment_method,
        created_at=order.created_at,
        updated_at=order.updated_at,
        items=[
            OrderItemResponse(
                id=item.id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
                applied_tax_rate=item.applied_tax_rate,
                status=item.status,
                notes=item.notes,
                modifiers=[
                    OrderItemModifierResponse(
                        id=m.id,
                        modifier_id=m.modifier_id,
                        applied_extra_price=m.applied_extra_price,
                    )
                    for m in item.modifiers
                ],
            )
            for item in order.items
        ],
        tables=[
            OrderTableResponse(table_id=ot.table_id, joined_at=ot.joined_at)
            for ot in order.tables
        ],
    )


@router.get("/", response_model=list[OrderResponse])
def list_open_orders(
    use_case: ListOpenOrdersUseCase = Depends(get_list_open_orders_use_case),
    _: TokenPayload = Depends(get_current_token_payload),
) -> list[OrderResponse]:
    return [_map_order(o) for o in use_case.execute()]


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: UUID,
    use_case: GetOrderUseCase = Depends(get_get_order_use_case),
    _: TokenPayload = Depends(get_current_token_payload),
) -> OrderResponse:
    return _map_order(use_case.execute(order_id))


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    body: CreateOrderRequest,
    use_case: CreateOrderUseCase = Depends(get_create_order_use_case),
    _: TokenPayload = Depends(get_current_token_payload),
) -> OrderResponse:
    order = use_case.execute(
        CreateOrderInput(
            waiter_user_id=body.waiter_user_id,
            table_ids=body.table_ids,
        )
    )
    return _map_order(order)


@router.post("/{order_id}/items", response_model=OrderItemResponse, status_code=status.HTTP_201_CREATED)
def add_order_item(
    order_id: UUID,
    body: AddOrderItemRequest,
    use_case: AddOrderItemUseCase = Depends(get_add_order_item_use_case),
    _: TokenPayload = Depends(get_current_token_payload),
) -> OrderItemResponse:
    from app.presentation.schemas.order import OrderItemModifierResponse
    item = use_case.execute(
        AddOrderItemInput(
            order_id=order_id,
            product_id=body.product_id,
            quantity=body.quantity,
            notes=body.notes,
            modifier_ids=body.modifier_ids,
        )
    )
    return OrderItemResponse(
        id=item.id,
        product_id=item.product_id,
        quantity=item.quantity,
        unit_price=item.unit_price,
        applied_tax_rate=item.applied_tax_rate,
        status=item.status,
        notes=item.notes,
        modifiers=[
            OrderItemModifierResponse(
                id=m.id,
                modifier_id=m.modifier_id,
                applied_extra_price=m.applied_extra_price,
            )
            for m in item.modifiers
        ],
    )


@router.patch("/{order_id}/items/{item_id}", response_model=OrderItemResponse)
def update_order_item(
    order_id: UUID,
    item_id: UUID,
    body: UpdateOrderItemRequest,
    use_case: UpdateOrderItemUseCase = Depends(get_update_order_item_use_case),
    _: TokenPayload = Depends(get_current_token_payload),
) -> OrderItemResponse:
    item = use_case.execute(
        UpdateOrderItemInput(
            order_id=order_id,
            item_id=item_id,
            quantity=body.quantity,
            notes=body.notes,
        )
    )
    return OrderItemResponse(
        id=item.id,
        product_id=item.product_id,
        quantity=item.quantity,
        unit_price=item.unit_price,
        applied_tax_rate=item.applied_tax_rate,
        status=item.status,
        notes=item.notes,
    )


@router.delete("/{order_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_order_item(
    order_id: UUID,
    item_id: UUID,
    use_case: RemoveOrderItemUseCase = Depends(get_remove_order_item_use_case),
    _: TokenPayload = Depends(get_current_token_payload),
) -> None:
    use_case.execute(RemoveOrderItemInput(order_id=order_id, item_id=item_id))


@router.patch("/{order_id}/items/{item_id}/status", response_model=OrderItemResponse)
def update_order_item_status(
    order_id: UUID,
    item_id: UUID,
    body: UpdateOrderItemStatusRequest,
    use_case: UpdateOrderItemStatusUseCase = Depends(get_update_order_item_status_use_case),
    _: TokenPayload = Depends(get_current_token_payload),
) -> OrderItemResponse:
    item = use_case.execute(
        UpdateOrderItemStatusInput(
            order_id=order_id,
            item_id=item_id,
            new_status=body.status,
        )
    )
    return OrderItemResponse(
        id=item.id,
        product_id=item.product_id,
        quantity=item.quantity,
        unit_price=item.unit_price,
        applied_tax_rate=item.applied_tax_rate,
        status=item.status,
        notes=item.notes,
    )


@router.post("/{order_id}/pay", response_model=OrderResponse)
def pay_order(
    order_id: UUID,
    body: PayOrderRequest,
    use_case: PayOrderUseCase = Depends(get_pay_order_use_case),
    _: TokenPayload = Depends(get_current_token_payload),
) -> OrderResponse:
    order = use_case.execute(
        PayOrderInput(
            order_id=order_id,
            payment_method=body.payment_method,
            tip=body.tip,
        )
    )
    return _map_order(order)


@router.post("/{order_id}/cancel", response_model=OrderResponse)
def cancel_order(
    order_id: UUID,
    body: CancelOrderRequest,
    use_case: CancelOrderUseCase = Depends(get_cancel_order_use_case),
    _: TokenPayload = Depends(get_current_token_payload),
) -> OrderResponse:
    order = use_case.execute(
        CancelOrderInput(order_id=order_id, reason=body.reason)
    )
    return _map_order(order)


@router.post("/{order_id}/discount", response_model=OrderResponse)
def apply_discount(
    order_id: UUID,
    body: ApplyDiscountRequest,
    use_case: ApplyDiscountUseCase = Depends(get_apply_discount_use_case),
    _: TokenPayload = Depends(require_manager_or_above),
) -> OrderResponse:
    order = use_case.execute(
        ApplyDiscountInput(
            order_id=order_id,
            amount=body.amount,
            reason=body.reason,
        )
    )
    return _map_order(order)


@router.post("/{order_id}/tables", status_code=status.HTTP_204_NO_CONTENT)
def assign_table(
    order_id: UUID,
    body: AssignTableRequest,
    use_case: AssignTableUseCase = Depends(get_assign_table_use_case),
    _: TokenPayload = Depends(get_current_token_payload),
) -> None:
    use_case.execute(AssignTableInput(order_id=order_id, table_id=body.table_id))


@router.delete("/{order_id}/tables/{table_id}", status_code=status.HTTP_204_NO_CONTENT)
def release_table(
    order_id: UUID,
    table_id: UUID,
    use_case: ReleaseTableUseCase = Depends(get_release_table_use_case),
    _: TokenPayload = Depends(get_current_token_payload),
) -> None:
    use_case.execute(ReleaseTableInput(order_id=order_id, table_id=table_id))
