from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ── Categories ──────────────────────────────────────────────────────────────

class CategoryCreate(BaseModel):
    name: str = Field(..., max_length=150)
    description: Optional[str] = None
    sort_order: Optional[int] = Field(None, ge=0)


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=150)
    description: Optional[str] = None
    sort_order: Optional[int] = Field(None, ge=0)


class CategoryResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    sort_order: Optional[int]

    model_config = {"from_attributes": True}


# ── Products ─────────────────────────────────────────────────────────────────

class ProductCreate(BaseModel):
    category_id: UUID
    name: str = Field(..., max_length=150)
    base_price: Decimal = Field(..., ge=Decimal("0"), decimal_places=4)
    is_available: bool = True
    sort_order: Optional[int] = Field(None, ge=0)
    tax_rate_id: Optional[UUID] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=150)
    is_available: Optional[bool] = None
    sort_order: Optional[int] = Field(None, ge=0)
    category_id: Optional[UUID] = None
    tax_rate_id: Optional[UUID] = None


class ProductPriceUpdate(BaseModel):
    base_price: Decimal = Field(..., ge=Decimal("0"), decimal_places=4)


class ProductResponse(BaseModel):
    id: UUID
    category_id: UUID
    name: str
    base_price: Decimal
    is_available: bool
    sort_order: Optional[int]
    tax_rate_id: Optional[UUID]

    model_config = {"from_attributes": True}


# ── Modifiers ────────────────────────────────────────────────────────────────

class ModifierCreate(BaseModel):
    name: str = Field(..., max_length=150)
    extra_price: Decimal = Field(Decimal("0.0"), ge=Decimal("0"), decimal_places=4)


class ModifierUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=150)
    extra_price: Optional[Decimal] = Field(None, ge=Decimal("0"), decimal_places=4)


class ModifierResponse(BaseModel):
    id: UUID
    product_id: UUID
    name: str
    extra_price: Decimal

    model_config = {"from_attributes": True}
