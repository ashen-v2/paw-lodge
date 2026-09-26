from uuid import UUID

from fastapi import APIRouter, status

from app.core.dependencies import CurrentUser, DbSession
from app.core.responses import error_responses
from app.schemas.visit import VisitCreate, VisitRead, VisitUpdate
from app.services.visits import create_visit, delete_visit, get_visit, list_visits, serialize_visit, update_visit

router = APIRouter(prefix="/visits", tags=["Visits"])


@router.post(
    "",
    response_model=VisitRead,
    status_code=status.HTTP_201_CREATED,
    responses=error_responses(400, 401, 404, 422),
    summary="Record a visit and calculate its total",
)
def create(payload: VisitCreate, current_user: CurrentUser, db: DbSession) -> VisitRead:
    return create_visit(db, current_user, payload)


@router.get(
    "",
    response_model=list[VisitRead],
    responses=error_responses(401),
    summary="List visits",
)
def list_all(current_user: CurrentUser, db: DbSession) -> list[VisitRead]:
    return list_visits(db, current_user.practice_id)


@router.get(
    "/{visit_id}",
    response_model=VisitRead,
    responses=error_responses(401, 404),
    summary="Get a visit",
)
def get_one(visit_id: UUID, current_user: CurrentUser, db: DbSession) -> VisitRead:
    return serialize_visit(get_visit(db, current_user.practice_id, visit_id))


@router.patch(
    "/{visit_id}",
    response_model=VisitRead,
    responses=error_responses(400, 401, 404, 422),
    summary="Update a visit",
)
def update(visit_id: UUID, payload: VisitUpdate, current_user: CurrentUser, db: DbSession) -> VisitRead:
    return update_visit(db, current_user, visit_id, payload)


@router.delete(
    "/{visit_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=error_responses(401, 404),
    summary="Delete a visit",
)
def delete(visit_id: UUID, current_user: CurrentUser, db: DbSession) -> None:
    delete_visit(db, current_user, visit_id)
