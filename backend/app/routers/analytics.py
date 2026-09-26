from datetime import date

from fastapi import APIRouter, HTTPException, Query, status

from app.core.dependencies import CurrentUser, DbSession
from app.core.responses import error_responses
from app.schemas.analytics import DashboardRead, RevenuePoint, ServiceStat
from app.services.analytics import dashboard, revenue_by_day, service_statistics

router = APIRouter(prefix="/analytics", tags=["Analytics"])


def _check_range(start: date | None, end: date | None) -> None:
    if start is not None and end is not None and start > end:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="from must not be after to",
        )


@router.get(
    "/dashboard",
    response_model=DashboardRead,
    responses=error_responses(401),
    summary="Today and month-to-date practice totals",
)
def get_dashboard(current_user: CurrentUser, db: DbSession) -> DashboardRead:
    return dashboard(db, current_user.practice_id)


@router.get(
    "/revenue",
    response_model=list[RevenuePoint],
    responses=error_responses(400, 401, 422),
    summary="Daily payment revenue",
)
def get_revenue(
    current_user: CurrentUser,
    db: DbSession,
    from_date: date | None = Query(default=None, alias="from"),
    to_date: date | None = Query(default=None, alias="to"),
) -> list[RevenuePoint]:
    _check_range(from_date, to_date)
    return revenue_by_day(db, current_user.practice_id, from_date, to_date)


@router.get(
    "/services",
    response_model=list[ServiceStat],
    responses=error_responses(400, 401, 422),
    summary="Service usage from visit item snapshots",
)
def get_service_stats(
    current_user: CurrentUser,
    db: DbSession,
    from_date: date | None = Query(default=None, alias="from"),
    to_date: date | None = Query(default=None, alias="to"),
) -> list[ServiceStat]:
    _check_range(from_date, to_date)
    return service_statistics(db, current_user.practice_id, from_date, to_date)
