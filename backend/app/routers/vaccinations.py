from datetime import date
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select

from app.core.dependencies import CurrentUser, DbSession
from app.core.responses import error_responses
from app.core.tenancy import get_owned
from app.models.pet import Pet
from app.models.vaccination import Vaccination
from app.models.visit import Visit
from app.schemas.vaccination import VaccinationCreate, VaccinationRead, VaccinationUpdate
from app.services.analytics import upcoming_vaccinations

router = APIRouter(prefix="/vaccinations", tags=["Vaccinations"])


def _validate_links(db, practice_id: UUID, pet_id: UUID, visit_id: UUID | None) -> None:
    get_owned(db, Pet, pet_id, practice_id, "Pet not found")
    if visit_id is None:
        return
    visit = get_owned(db, Visit, visit_id, practice_id, "Visit not found")
    if visit.pet_id != pet_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Visit does not belong to this pet",
        )


def _ensure_dates(administered: date, next_due: date | None) -> None:
    if next_due is not None and next_due < administered:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="next_due_date must not precede administered_date",
        )


@router.post(
    "",
    response_model=VaccinationRead,
    status_code=status.HTTP_201_CREATED,
    responses=error_responses(400, 401, 404, 422),
    summary="Record a vaccination",
)
def create_vaccination(
    payload: VaccinationCreate,
    current_user: CurrentUser,
    db: DbSession,
) -> Vaccination:
    _validate_links(db, current_user.practice_id, payload.pet_id, payload.visit_id)
    vaccination = Vaccination(practice_id=current_user.practice_id, **payload.model_dump())
    db.add(vaccination)
    db.commit()
    db.refresh(vaccination)
    return vaccination


@router.get(
    "",
    response_model=list[VaccinationRead],
    responses=error_responses(401),
    summary="List vaccinations",
)
def list_vaccinations(current_user: CurrentUser, db: DbSession) -> list[Vaccination]:
    statement = (
        select(Vaccination)
        .where(Vaccination.practice_id == current_user.practice_id)
        .order_by(Vaccination.administered_date.desc(), Vaccination.created_at.desc())
    )
    return list(db.scalars(statement).all())


@router.get(
    "/upcoming",
    response_model=list[VaccinationRead],
    responses=error_responses(401, 422),
    summary="Vaccinations due between today and today plus days",
)
def list_upcoming(
    current_user: CurrentUser,
    db: DbSession,
    days: int = Query(default=30, ge=0, le=3650),
) -> list[Vaccination]:
    return upcoming_vaccinations(db, current_user.practice_id, days=days)


@router.get(
    "/{vaccination_id}",
    response_model=VaccinationRead,
    responses=error_responses(401, 404),
    summary="Get a vaccination",
)
def get_vaccination(vaccination_id: UUID, current_user: CurrentUser, db: DbSession) -> Vaccination:
    return get_owned(db, Vaccination, vaccination_id, current_user.practice_id, "Vaccination not found")


@router.patch(
    "/{vaccination_id}",
    response_model=VaccinationRead,
    responses=error_responses(400, 401, 404, 422),
    summary="Update a vaccination",
)
def update_vaccination(
    vaccination_id: UUID,
    payload: VaccinationUpdate,
    current_user: CurrentUser,
    db: DbSession,
) -> Vaccination:
    vaccination = get_owned(db, Vaccination, vaccination_id, current_user.practice_id, "Vaccination not found")
    changes = payload.model_dump(exclude_unset=True)
    pet_id = changes.get("pet_id", vaccination.pet_id)
    visit_id = changes["visit_id"] if "visit_id" in changes else vaccination.visit_id
    administered = changes.get("administered_date", vaccination.administered_date)
    next_due = changes["next_due_date"] if "next_due_date" in changes else vaccination.next_due_date
    _validate_links(db, current_user.practice_id, pet_id, visit_id)
    _ensure_dates(administered, next_due)
    for key, value in changes.items():
        setattr(vaccination, key, value)
    db.commit()
    db.refresh(vaccination)
    return vaccination


@router.delete(
    "/{vaccination_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=error_responses(401, 404),
    summary="Delete a vaccination",
)
def delete_vaccination(vaccination_id: UUID, current_user: CurrentUser, db: DbSession) -> None:
    vaccination = get_owned(db, Vaccination, vaccination_id, current_user.practice_id, "Vaccination not found")
    db.delete(vaccination)
    db.commit()
