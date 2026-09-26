from datetime import date, datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.types import Money


class PetCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    owner_id: UUID
    name: str = Field(min_length=1, max_length=255)
    species: str = Field(min_length=1, max_length=100)
    breed: str | None = Field(default=None, max_length=100)
    sex: str | None = Field(default=None, max_length=20)
    date_of_birth: date | None = None
    color: str | None = Field(default=None, max_length=50)
    notes: str | None = None

    @field_validator("name", "species")
    @classmethod
    def strip_required(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("must not be blank")
        return cleaned

    @field_validator("breed", "sex", "color", "notes")
    @classmethod
    def blank_to_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class PetUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    owner_id: UUID | None = None
    name: str | None = Field(default=None, min_length=1, max_length=255)
    species: str | None = Field(default=None, min_length=1, max_length=100)
    breed: str | None = Field(default=None, max_length=100)
    sex: str | None = Field(default=None, max_length=20)
    date_of_birth: date | None = None
    color: str | None = Field(default=None, max_length=50)
    notes: str | None = None

    @field_validator("name", "species")
    @classmethod
    def strip_required(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("must not be blank")
        return cleaned

    @field_validator("breed", "sex", "color", "notes")
    @classmethod
    def blank_to_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class PetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    practice_id: UUID
    owner_id: UUID
    name: str
    species: str
    breed: str | None
    sex: str | None
    date_of_birth: date | None
    color: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime


class TimelineEvent(BaseModel):
    type: Literal["visit", "vaccination", "payment"]
    date: date
    title: str
    details: dict[str, Any]


class PetHistory(BaseModel):
    pet: PetRead
    timeline: list[TimelineEvent]
