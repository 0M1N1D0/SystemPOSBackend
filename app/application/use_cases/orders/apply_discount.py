from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from uuid import UUID

from app.domain.entities.order import Order
from app.domain.enums import AuditAction, RoleName
from app.domain.exceptions import (
    InsufficientPermissionsError,
    OrderAlreadyClosedError,
    OrderNotFoundError,
)
from app.domain.repositories.i_order_repository import IOrderRepository
from app.domain.services.i_audit_log_service import IAuditLogService


@dataclass
class ApplyDiscountInput:
    order_id: UUID
    amount: Decimal
    reason: Optional[str] = None


class ApplyDiscountUseCase:
    def __init__(
        self,
        order_repo: IOrderRepository,
        audit_service: IAuditLogService,
        actor_user_id: UUID,
        actor_role: RoleName,
    ) -> None:
        self._order_repo = order_repo
        self._audit = audit_service
        self._actor = actor_user_id
        self._actor_role = actor_role

    def execute(self, input_data: ApplyDiscountInput) -> Order:
        if self._actor_role not in (RoleName.ADMIN, RoleName.MANAGER):
            raise InsufficientPermissionsError(
                "Only ADMIN or MANAGER can apply discounts"
            )

        order = self._order_repo.find_by_id(input_data.order_id)
        if order is None:
            raise OrderNotFoundError(f"Order {input_data.order_id} not found")
        if not order.is_open():
            raise OrderAlreadyClosedError(
                f"Order {input_data.order_id} is {order.status.value} and cannot be modified"
            )
        if input_data.amount < Decimal("0"):
            raise ValueError("Discount amount must be >= 0")

        order.discount = input_data.amount
        order.items = self._order_repo.find_items_by_order(order.id)
        order.recalculate_totals()
        order.updated_at = datetime.now(timezone.utc)
        updated_order = self._order_repo.update(order)

        self._audit.log(
            user_id=self._actor,
            action=AuditAction.DISCOUNT_APPLIED,
            details={
                "order_id": str(input_data.order_id),
                "amount": str(input_data.amount),
                "reason": input_data.reason,
            },
        )
        updated_order.items = order.items
        return updated_order
