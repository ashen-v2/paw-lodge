from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class VaccinationCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    pet_id: UUID
    visit_id: UUID | None = None
    vaccine_name: str = Field(min_length=1, max_length=255)
    administered_date: date
    next_due_date: date | None = None
    batch_number: str | None = Field(default=None, max_length=100)
    notes: str | None = None

    @field_validator("vaccine_name")
    @classmethod
    def strip_name(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("must not be blank")
        return cleaned

    @field_validator("batch_number", "notes")
    @classmethod
    def blank_to_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None

    @model_validator(mode="after")
    def due_not_before_administered(self) -> "VaccinationCreate":
        if self.next_due_date is not None and self.next_due_date < self.administered_date:
            raise ValueError("next_due_date must not precede administered_date")
        return self


class VaccinationUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    pet_id: UUID | None = None
    visit_id: UUID | None = None
    vaccine_name: str | None = Field(default=None, min_length=1, max_length=255)
    administered_date: date | None = None
    next_due_date: date | None = None
    batch_number: str | None = Field(default=None, max_length=100)
    notes: str | None = None

    @field_validator("vaccine_name")
    @classmethod
    def strip_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("must not be blank")
        return cleaned

    @field_validator("batch_number", "notes")
    @classmethod
    def blank_to_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None

    @model_validator(mode="after")
    def due_not_before_administered(self) -> "VaccinationUpdate":
        if (
            self.next_due_date is not None
            and self.administered_date is not None
            and self.next_due_date < self.administered_date
        ):
            raise ValueError("next_due_date must not precede administered_date")
        return self


class VaccinationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    practice_id: UUID
    pet_id: UUID
    visit_id: UUID | None
    vaccine_name: str
    administered_date: date
    next_due_date: date | None
    batch_number: str | None
    notes: str | None
    created_at: datetime
