from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class TaxRateCreate(BaseModel):
    name: str = Field(..., max_length=100)
    rate: Decimal = Field(..., ge=Decimal("0"), le=Decimal("1"), decimal_places=4)
    is_default: bool = False


class TaxRateUpdate(BaseModel):
    name: str | None = Field(None, max_length=100)
    rate: Decimal | None = Field(None, ge=Decimal("0"), le=Decimal("1"), decimal_places=4)


class TaxRateResponse(BaseModel):
    id: UUID
    name: str
    rate: Decimal
    is_default: bool
    is_active: bool

    model_config = {"from_attributes": True}
