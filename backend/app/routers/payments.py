from uuid import UUID

from fastapi import APIRouter, status

from app.core.dependencies import CurrentUser, DbSession
from app.core.responses import error_responses
from app.models.payment import Payment
from app.schemas.payment import PaymentCreate, PaymentRead
from app.services.visits import list_payments, payment_for_visit, record_payment

router = APIRouter(prefix="/payments", tags=["Payments"])
visit_payment_router = APIRouter(tags=["Payments"])


@router.post(
    "",
    response_model=PaymentRead,
    status_code=status.HTTP_201_CREATED,
    responses=error_responses(400, 401, 404, 409, 422),
    summary="Record a payment for a visit",
)
def create_payment(payload: PaymentCreate, current_user: CurrentUser, db: DbSession) -> Payment:
    return record_payment(db, current_user, payload)


@router.get(
    "",
    response_model=list[PaymentRead],
    responses=error_responses(401),
    summary="List payments",
)
def get_payments(current_user: CurrentUser, db: DbSession) -> list[Payment]:
    return list_payments(db, current_user.practice_id)


@visit_payment_router.get(
    "/visits/{visit_id}/payment",
    response_model=PaymentRead,
    responses=error_responses(401, 404),
    summary="Get the payment recorded for a visit",
)
def get_visit_payment(visit_id: UUID, current_user: CurrentUser, db: DbSession) -> Payment:
    return payment_for_visit(db, current_user.practice_id, visit_id)
