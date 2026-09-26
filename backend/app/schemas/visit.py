from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core.money import MAX_MONEY, quantize_money
from app.schemas.payment import PaymentRead
from app.schemas.types import Money


class VisitItemCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    service_id: UUID | None = None
    description: str | None = Field(default=None, max_length=255)
    quantity: int = Field(gt=0)
    unit_price: Decimal | None = Field(default=None, ge=0, le=MAX_MONEY)

    @field_validator("description")
    @classmethod
    def strip_description(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None

    @field_validator("unit_price")
    @classmethod
    def money(cls, value: Decimal | None) -> Decimal | None:
        if value is None:
            return None
        return quantize_money(value)

    @model_validator(mode="after")
    def one_off_requires_price(self) -> "VisitItemCreate":
        if self.service_id is None:
            if not self.description:
                raise ValueError("description is required when service_id is omitted")
            if self.unit_price is None:
                raise ValueError("unit_price is required when service_id is omitted")
        return self


class VisitCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    pet_id: UUID
    visit_date: date
    diagnosis: str | None = None
    notes: str | None = None
    follow_up_date: date | None = None
    items: list[VisitItemCreate] = Field(default_factory=list)

    @field_validator("diagnosis", "notes")
    @classmethod
    def blank_to_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class VisitUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    pet_id: UUID | None = None
    visit_date: date | None = None
    diagnosis: str | None = None
    notes: str | None = None
    follow_up_date: date | None = None
    items: list[VisitItemCreate] | None = None

    @field_validator("diagnosis", "notes")
    @classmethod
    def blank_to_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class VisitItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    service_id: UUID | None
    description: str
    quantity: int
    unit_price: Money
    subtotal: Money


class VisitRead(BaseModel):
    id: UUID
    practice_id: UUID
    pet_id: UUID
    user_id: UUID
    visit_date: date
    diagnosis: str | None
    notes: str | None
    follow_up_date: date | None
    items: list[VisitItemRead]
    total: Money
    outstanding: Money
    payment: PaymentRead | None
    created_at: datetime
    updated_at: datetime
