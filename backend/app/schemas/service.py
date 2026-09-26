from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.money import MAX_MONEY, quantize_money
from app.schemas.types import Money


class ServiceCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    price: Decimal = Field(ge=0, le=MAX_MONEY)
    is_active: bool = True

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("must not be blank")
        return cleaned

    @field_validator("description")
    @classmethod
    def blank_to_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None

    @field_validator("price")
    @classmethod
    def money(cls, value: Decimal) -> Decimal:
        return quantize_money(value)


class ServiceUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    price: Decimal | None = Field(default=None, ge=0, le=MAX_MONEY)
    is_active: bool | None = None

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("must not be blank")
        return cleaned

    @field_validator("description")
    @classmethod
    def blank_to_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None

    @field_validator("price")
    @classmethod
    def money(cls, value: Decimal | None) -> Decimal | None:
        if value is None:
            return None
        return quantize_money(value)


class ServiceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    practice_id: UUID
    name: str
    description: str | None
    price: Money
    is_active: bool
    created_at: datetime
    updated_at: datetime
