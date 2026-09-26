"""Import every model so metadata and Alembic see the full schema."""

from app.models.owner import Owner
from app.models.payment import Payment
from app.models.pet import Pet
from app.models.practice import Practice
from app.models.service import Service
from app.models.user import User
from app.models.vaccination import Vaccination
from app.models.visit import Visit, VisitItem

__all__ = [
    "Owner",
    "Payment",
    "Pet",
    "Practice",
    "Service",
    "User",
    "Vaccination",
    "Visit",
    "VisitItem",
]
