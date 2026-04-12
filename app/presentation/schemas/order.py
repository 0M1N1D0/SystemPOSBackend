from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.enums import OrderItemStatus, OrderStatus, PaymentMethod


# --- OrderItemModifier ---

class OrderItemModifierResponse(BaseModel):
    id: UUID
    modifier_id: UUID
    applied_extra_price: Decimal


# --- OrderItem ---

class AddOrderItemRequest(BaseModel):
    product_id: UUID
    quantity: int = Field(gt=0)
    notes: Optional[str] = None
    modifier_ids: list[UUID] = Field(default_factory=list)


class UpdateOrderItemRequest(BaseModel):
    quantity: Optional[int] = Field(default=None, gt=0)
    notes: Optional[str] = None


class UpdateOrderItemStatusRequest(BaseModel):
    status: OrderItemStatus


class OrderItemResponse(BaseModel):
    id: UUID
    product_id: UUID
    quantity: int
    unit_price: Decimal
    applied_tax_rate: Decimal
    status: OrderItemStatus
    notes: Optional[str]
    modifiers: list[OrderItemModifierResponse] = Field(default_factory=list)


# --- OrderTable ---

class OrderTableResponse(BaseModel):
    table_id: UUID
    joined_at: datetime


# --- Order ---

class CreateOrderRequest(BaseModel):
    waiter_user_id: UUID
    table_ids: list[UUID] = Field(default_factory=list)


class PayOrderRequest(BaseModel):
    payment_method: PaymentMethod
    tip: Decimal = Field(default=Decimal("0"), ge=0)


class CancelOrderRequest(BaseModel):
    reason: Optional[str] = None


class ApplyDiscountRequest(BaseModel):
    amount: Decimal = Field(ge=0)
    reason: Optional[str] = None


class AssignTableRequest(BaseModel):
    table_id: UUID


class OrderResponse(BaseModel):
    id: UUID
    user_id: UUID
    subtotal: Decimal
    taxes: Decimal
    tip: Decimal
    discount: Decimal
    total_amount: Decimal
    status: OrderStatus
    payment_method: Optional[PaymentMethod]
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemResponse] = Field(default_factory=list)
    tables: list[OrderTableResponse] = Field(default_factory=list)
