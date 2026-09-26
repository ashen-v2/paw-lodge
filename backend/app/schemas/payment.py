from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.money import MAX_MONEY, quantize_money
from app.schemas.types import Money


class PaymentCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    visit_id: UUID
    amount: Decimal = Field(gt=0, le=MAX_MONEY)
    payment_method: Literal["cash", "other"] = "cash"
    paid_at: datetime | None = None

    @field_validator("amount")
    @classmethod
    def money(cls, value: Decimal) -> Decimal:
        quantized = quantize_money(value)
        if quantized <= 0:
            raise ValueError("amount must be greater than 0")
        return quantized


class PaymentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    practice_id: UUID
    visit_id: UUID
    amount: Money
    payment_method: str
    paid_at: datetime
