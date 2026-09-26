from uuid import UUID

from fastapi import APIRouter, Query, status
from sqlalchemy import select

from app.core.dependencies import CurrentUser, DbSession
from app.core.responses import error_responses
from app.core.tenancy import get_owned
from app.models.service import Service
from app.schemas.service import ServiceCreate, ServiceRead, ServiceUpdate

router = APIRouter(prefix="/services", tags=["Services"])


@router.post(
    "",
    response_model=ServiceRead,
    status_code=status.HTTP_201_CREATED,
    responses=error_responses(401, 422),
    summary="Add a service to the catalog",
)
def create_service(payload: ServiceCreate, current_user: CurrentUser, db: DbSession) -> Service:
    service = Service(practice_id=current_user.practice_id, **payload.model_dump())
    db.add(service)
    db.commit()
    db.refresh(service)
    return service


@router.get(
    "",
    response_model=list[ServiceRead],
    responses=error_responses(401),
    summary="List services",
)
def list_services(
    current_user: CurrentUser,
    db: DbSession,
    include_inactive: bool = Query(default=False, description="Include deactivated services"),
) -> list[Service]:
    statement = select(Service).where(Service.practice_id == current_user.practice_id)
    if not include_inactive:
        statement = statement.where(Service.is_active.is_(True))
    statement = statement.order_by(Service.name, Service.created_at)
    return list(db.scalars(statement).all())


@router.get(
    "/{service_id}",
    response_model=ServiceRead,
    responses=error_responses(401, 404),
    summary="Get a service",
)
def get_service(service_id: UUID, current_user: CurrentUser, db: DbSession) -> Service:
    return get_owned(db, Service, service_id, current_user.practice_id, "Service not found")


@router.patch(
    "/{service_id}",
    response_model=ServiceRead,
    responses=error_responses(401, 404, 422),
    summary="Update a service",
)
def update_service(
    service_id: UUID,
    payload: ServiceUpdate,
    current_user: CurrentUser,
    db: DbSession,
) -> Service:
    service = get_owned(db, Service, service_id, current_user.practice_id, "Service not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(service, key, value)
    db.commit()
    db.refresh(service)
    return service


@router.delete(
    "/{service_id}",
    response_model=ServiceRead,
    responses=error_responses(401, 404),
    summary="Deactivate a service",
)
def deactivate_service(service_id: UUID, current_user: CurrentUser, db: DbSession) -> Service:
    service = get_owned(db, Service, service_id, current_user.practice_id, "Service not found")
    service.is_active = False
    db.commit()
    db.refresh(service)
    return service
