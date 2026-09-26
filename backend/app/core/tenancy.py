from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import Select, select
from sqlalchemy.orm import Session


def owned_query(model, practice_id: UUID) -> Select:
    return select(model).where(model.practice_id == practice_id)


def get_owned(db: Session, model, object_id: UUID, practice_id: UUID, detail: str, *options):
    statement = owned_query(model, practice_id).where(model.id == object_id)
    if options:
        statement = statement.options(*options)
    obj = db.scalar(statement)
    if obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
    return obj
