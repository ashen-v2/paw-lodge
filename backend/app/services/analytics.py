"""SQL aggregates for dashboard, revenue, and catalog usage.

These functions take an authenticated practice id. They are the supported
entry points for a future assistant; they do not expose unrestricted queries.
"""

from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal
from uuid import UUID

from sqlalchemy import Date, cast, func, select
from sqlalchemy.orm import Session

from app.core.money import quantize_money
from app.models.payment import Payment
from app.models.pet import Pet
from app.models.vaccination import Vaccination
from app.models.visit import Visit, VisitItem
from app.schemas.analytics import DashboardRead, MonthStats, RevenuePoint, ServiceStat, TodayStats

UPCOMING_WINDOW_DAYS = 30


def utc_today() -> date:
    return datetime.now(timezone.utc).date()


def _day_start(value: date) -> datetime:
    return datetime.combine(value, time.min, tzinfo=timezone.utc)


def _month_bounds(day: date) -> tuple[date, date]:
    start = day.replace(day=1)
    if start.month == 12:
        end = date(start.year + 1, 1, 1)
    else:
        end = date(start.year, start.month + 1, 1)
    return start, end


def _sum_payments(db: Session, practice_id: UUID, start: datetime, end: datetime) -> Decimal:
    total = db.scalar(
        select(func.coalesce(func.sum(Payment.amount), 0)).where(
            Payment.practice_id == practice_id,
            Payment.paid_at >= start,
            Payment.paid_at < end,
        )
    )
    return quantize_money(total or 0)


def _count_visits(db: Session, practice_id: UUID, start: date, end: date | None = None) -> int:
    statement = select(func.count()).select_from(Visit).where(
        Visit.practice_id == practice_id,
        Visit.visit_date >= start,
    )
    if end is None:
        statement = statement.where(Visit.visit_date == start)
    else:
        statement = statement.where(Visit.visit_date < end)
    return int(db.scalar(statement) or 0)


def upcoming_vaccinations(
    db: Session,
    practice_id: UUID,
    *,
    days: int = UPCOMING_WINDOW_DAYS,
    today: date | None = None,
) -> list[Vaccination]:
    current = today or utc_today()
    last = current + timedelta(days=days)
    statement = (
        select(Vaccination)
        .where(
            Vaccination.practice_id == practice_id,
            Vaccination.next_due_date.is_not(None),
            Vaccination.next_due_date >= current,
            Vaccination.next_due_date <= last,
        )
        .order_by(Vaccination.next_due_date, Vaccination.vaccine_name)
    )
    return list(db.scalars(statement).all())


def count_upcoming_vaccinations(
    db: Session,
    practice_id: UUID,
    *,
    days: int = UPCOMING_WINDOW_DAYS,
    today: date | None = None,
) -> int:
    current = today or utc_today()
    last = current + timedelta(days=days)
    return int(
        db.scalar(
            select(func.count())
            .select_from(Vaccination)
            .where(
                Vaccination.practice_id == practice_id,
                Vaccination.next_due_date.is_not(None),
                Vaccination.next_due_date >= current,
                Vaccination.next_due_date <= last,
            )
        )
        or 0
    )


def dashboard(db: Session, practice_id: UUID) -> DashboardRead:
    today = utc_today()
    month_start, next_month = _month_bounds(today)
    today_start = _day_start(today)
    tomorrow = today_start + timedelta(days=1)
    month_start_dt = _day_start(month_start)
    next_month_dt = _day_start(next_month)

    new_pets = int(
        db.scalar(
            select(func.count())
            .select_from(Pet)
            .where(
                Pet.practice_id == practice_id,
                Pet.created_at >= month_start_dt,
                Pet.created_at < next_month_dt,
            )
        )
        or 0
    )
    vaccinations = int(
        db.scalar(
            select(func.count())
            .select_from(Vaccination)
            .where(
                Vaccination.practice_id == practice_id,
                Vaccination.administered_date >= month_start,
                Vaccination.administered_date < next_month,
            )
        )
        or 0
    )
    return DashboardRead(
        today=TodayStats(
            visits=_count_visits(db, practice_id, today),
            revenue=_sum_payments(db, practice_id, today_start, tomorrow),
        ),
        month=MonthStats(
            visits=_count_visits(db, practice_id, month_start, next_month),
            revenue=_sum_payments(db, practice_id, month_start_dt, next_month_dt),
            new_pets=new_pets,
            vaccinations=vaccinations,
        ),
        upcoming_vaccinations=count_upcoming_vaccinations(db, practice_id, today=today),
    )


def revenue_by_day(
    db: Session,
    practice_id: UUID,
    start: date | None = None,
    end: date | None = None,
) -> list[RevenuePoint]:
    today = utc_today()
    if start is None and end is None:
        start, next_month = _month_bounds(today)
        end = next_month - timedelta(days=1)
    elif start is None:
        start = end
    elif end is None:
        end = start

    start_dt = _day_start(start)
    end_dt = _day_start(end) + timedelta(days=1)
    paid_day = cast(func.timezone("UTC", Payment.paid_at), Date)
    rows = db.execute(
        select(
            paid_day.label("day"),
            func.coalesce(func.sum(Payment.amount), 0).label("revenue"),
        )
        .where(
            Payment.practice_id == practice_id,
            Payment.paid_at >= start_dt,
            Payment.paid_at < end_dt,
        )
        .group_by(paid_day)
        .order_by(paid_day)
    ).all()
    return [
        RevenuePoint(date=row.day, revenue=quantize_money(row.revenue or 0))
        for row in rows
    ]


def service_statistics(
    db: Session,
    practice_id: UUID,
    start: date | None = None,
    end: date | None = None,
) -> list[ServiceStat]:
    statement = (
        select(
            VisitItem.description.label("service"),
            func.coalesce(func.sum(VisitItem.quantity), 0).label("count"),
            func.coalesce(func.sum(VisitItem.subtotal), 0).label("revenue"),
        )
        .join(Visit, Visit.id == VisitItem.visit_id)
        .where(Visit.practice_id == practice_id)
        .group_by(VisitItem.description)
        .order_by(func.sum(VisitItem.subtotal).desc(), VisitItem.description)
    )
    if start is not None:
        statement = statement.where(Visit.visit_date >= start)
    if end is not None:
        statement = statement.where(Visit.visit_date <= end)
    rows = db.execute(statement).all()
    return [
        ServiceStat(
            service=row.service,
            count=int(row.count or 0),
            revenue=quantize_money(row.revenue or 0),
        )
        for row in rows
    ]
