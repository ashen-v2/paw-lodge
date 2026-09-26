from datetime import date

from pydantic import BaseModel

from app.schemas.types import Money


class TodayStats(BaseModel):
    visits: int
    revenue: Money


class MonthStats(BaseModel):
    visits: int
    revenue: Money
    new_pets: int
    vaccinations: int


class DashboardRead(BaseModel):
    today: TodayStats
    month: MonthStats
    upcoming_vaccinations: int


class RevenuePoint(BaseModel):
    date: date
    revenue: Money


class ServiceStat(BaseModel):
    service: str
    count: int
    revenue: Money
