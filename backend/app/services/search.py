"""Tenant-scoped search used by the API and safe for a later assistant to call."""

from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.owner import Owner
from app.models.pet import Pet


def contains_pattern(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def search_owners(db: Session, practice_id: UUID, search: str | None) -> list[Owner]:
    statement = select(Owner).where(Owner.practice_id == practice_id)
    if search and search.strip():
        pattern = contains_pattern(search.strip())
        statement = statement.where(
            or_(
                Owner.name.ilike(pattern, escape="\\"),
                Owner.phone.ilike(pattern, escape="\\"),
                Owner.email.ilike(pattern, escape="\\"),
            )
        )
    statement = statement.order_by(Owner.name, Owner.created_at)
    return list(db.scalars(statement).all())


def search_pets(
    db: Session,
    practice_id: UUID,
    search: str | None = None,
    species: str | None = None,
) -> list[Pet]:
    statement = select(Pet).where(Pet.practice_id == practice_id)
    if search and search.strip():
        statement = statement.where(Pet.name.ilike(contains_pattern(search.strip()), escape="\\"))
    if species and species.strip():
        statement = statement.where(func.lower(Pet.species) == species.strip().lower())
    statement = statement.order_by(Pet.name, Pet.created_at)
    return list(db.scalars(statement).all())
