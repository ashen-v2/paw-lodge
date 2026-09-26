from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select

from app.core.dependencies import CurrentUser, DbSession
from app.core.responses import error_responses
from app.core.tenancy import get_owned
from app.models.owner import Owner
from app.models.pet import Pet
from app.models.vaccination import Vaccination
from app.models.visit import Visit
from app.schemas.pet import PetCreate, PetHistory, PetRead, PetUpdate
from app.schemas.vaccination import VaccinationRead
from app.schemas.visit import VisitRead
from app.services.search import search_pets
from app.services.visits import list_visits, pet_history

router = APIRouter(prefix="/pets", tags=["Pets"])


def _owner_or_404(db, practice_id: UUID, owner_id: UUID) -> Owner:
    return get_owned(db, Owner, owner_id, practice_id, "Owner not found")


@router.post(
    "",
    response_model=PetRead,
    status_code=status.HTTP_201_CREATED,
    responses=error_responses(401, 404, 422),
    summary="Register a pet",
)
def create_pet(payload: PetCreate, current_user: CurrentUser, db: DbSession) -> Pet:
    _owner_or_404(db, current_user.practice_id, payload.owner_id)
    pet = Pet(practice_id=current_user.practice_id, **payload.model_dump())
    db.add(pet)
    db.commit()
    db.refresh(pet)
    return pet


@router.get(
    "",
    response_model=list[PetRead],
    responses=error_responses(401, 422),
    summary="List pets",
)
def list_pets(
    current_user: CurrentUser,
    db: DbSession,
    search: str | None = Query(default=None, description="Match pet name"),
    species: str | None = Query(default=None, description="Case-insensitive species, for example dog"),
) -> list[Pet]:
    return search_pets(db, current_user.practice_id, search, species)


@router.get(
    "/{pet_id}/history",
    response_model=PetHistory,
    responses=error_responses(401, 404),
    summary="Pet timeline, newest first",
)
def get_pet_history(pet_id: UUID, current_user: CurrentUser, db: DbSession) -> PetHistory:
    return pet_history(db, current_user.practice_id, pet_id)


@router.get(
    "/{pet_id}/visits",
    response_model=list[VisitRead],
    responses=error_responses(401, 404),
    summary="List visits for a pet",
)
def get_pet_visits(pet_id: UUID, current_user: CurrentUser, db: DbSession) -> list[VisitRead]:
    return list_visits(db, current_user.practice_id, pet_id)


@router.get(
    "/{pet_id}/vaccinations",
    response_model=list[VaccinationRead],
    responses=error_responses(401, 404),
    summary="List vaccinations for a pet",
)
def get_pet_vaccinations(pet_id: UUID, current_user: CurrentUser, db: DbSession) -> list[Vaccination]:
    get_owned(db, Pet, pet_id, current_user.practice_id, "Pet not found")
    statement = (
        select(Vaccination)
        .where(Vaccination.practice_id == current_user.practice_id, Vaccination.pet_id == pet_id)
        .order_by(Vaccination.administered_date.desc(), Vaccination.created_at.desc())
    )
    return list(db.scalars(statement).all())


@router.get(
    "/{pet_id}",
    response_model=PetRead,
    responses=error_responses(401, 404),
    summary="Get a pet",
)
def get_pet(pet_id: UUID, current_user: CurrentUser, db: DbSession) -> Pet:
    return get_owned(db, Pet, pet_id, current_user.practice_id, "Pet not found")


@router.patch(
    "/{pet_id}",
    response_model=PetRead,
    responses=error_responses(401, 404, 422),
    summary="Update a pet",
)
def update_pet(pet_id: UUID, payload: PetUpdate, current_user: CurrentUser, db: DbSession) -> Pet:
    pet = get_owned(db, Pet, pet_id, current_user.practice_id, "Pet not found")
    changes = payload.model_dump(exclude_unset=True)
    if "owner_id" in changes and changes["owner_id"] is not None:
        _owner_or_404(db, current_user.practice_id, changes["owner_id"])
    for key, value in changes.items():
        setattr(pet, key, value)
    db.commit()
    db.refresh(pet)
    return pet


@router.delete(
    "/{pet_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=error_responses(400, 401, 404),
    summary="Delete a pet",
)
def delete_pet(pet_id: UUID, current_user: CurrentUser, db: DbSession) -> None:
    pet = get_owned(db, Pet, pet_id, current_user.practice_id, "Pet not found")
    has_visit = db.scalar(select(Visit.id).where(Visit.pet_id == pet.id, Visit.practice_id == current_user.practice_id))
    has_vaccination = db.scalar(
        select(Vaccination.id).where(
            Vaccination.pet_id == pet.id,
            Vaccination.practice_id == current_user.practice_id,
        )
    )
    if has_visit is not None or has_vaccination is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pet has clinical records and cannot be deleted",
        )
    db.delete(pet)
    db.commit()
