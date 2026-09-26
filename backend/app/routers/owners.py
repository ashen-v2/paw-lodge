from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select

from app.core.dependencies import CurrentUser, DbSession
from app.core.responses import error_responses
from app.core.tenancy import get_owned
from app.models.owner import Owner
from app.models.pet import Pet
from app.schemas.owner import OwnerCreate, OwnerRead, OwnerUpdate
from app.services.search import search_owners

router = APIRouter(prefix="/owners", tags=["Owners"])


@router.post(
    "",
    response_model=OwnerRead,
    status_code=status.HTTP_201_CREATED,
    responses=error_responses(401, 422),
    summary="Create a pet owner",
)
def create_owner(payload: OwnerCreate, current_user: CurrentUser, db: DbSession) -> Owner:
    owner = Owner(practice_id=current_user.practice_id, **payload.model_dump())
    db.add(owner)
    db.commit()
    db.refresh(owner)
    return owner


@router.get(
    "",
    response_model=list[OwnerRead],
    responses=error_responses(401, 422),
    summary="List pet owners",
)
def list_owners(
    current_user: CurrentUser,
    db: DbSession,
    search: str | None = Query(default=None, description="Match name, phone, or email"),
) -> list[Owner]:
    return search_owners(db, current_user.practice_id, search)


@router.get(
    "/{owner_id}",
    response_model=OwnerRead,
    responses=error_responses(401, 404),
    summary="Get a pet owner",
)
def get_owner(owner_id: UUID, current_user: CurrentUser, db: DbSession) -> Owner:
    return get_owned(db, Owner, owner_id, current_user.practice_id, "Owner not found")


@router.patch(
    "/{owner_id}",
    response_model=OwnerRead,
    responses=error_responses(401, 404, 422),
    summary="Update a pet owner",
)
def update_owner(
    owner_id: UUID,
    payload: OwnerUpdate,
    current_user: CurrentUser,
    db: DbSession,
) -> Owner:
    owner = get_owned(db, Owner, owner_id, current_user.practice_id, "Owner not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(owner, key, value)
    db.commit()
    db.refresh(owner)
    return owner


@router.delete(
    "/{owner_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=error_responses(400, 401, 404),
    summary="Delete a pet owner",
)
def delete_owner(owner_id: UUID, current_user: CurrentUser, db: DbSession) -> None:
    owner = get_owned(db, Owner, owner_id, current_user.practice_id, "Owner not found")
    has_pets = db.scalar(
        select(Pet.id).where(Pet.owner_id == owner.id, Pet.practice_id == current_user.practice_id)
    )
    if has_pets is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Owner has pets and cannot be deleted",
        )
    db.delete(owner)
    db.commit()
