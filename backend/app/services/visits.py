"""Visit creation, totals, payments, and pet history.

Totals are always calculated here from stored line items. Catalog prices are
copied onto the line when the visit is recorded and are not read again later.
"""

from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.core.money import quantize_money
from app.core.tenancy import get_owned
from app.models.payment import Payment
from app.models.pet import Pet
from app.models.service import Service
from app.models.user import User
from app.models.vaccination import Vaccination
from app.models.visit import Visit, VisitItem
from app.schemas.payment import PaymentCreate, PaymentRead
from app.schemas.pet import PetHistory, PetRead, TimelineEvent
from app.schemas.visit import VisitCreate, VisitItemCreate, VisitItemRead, VisitRead, VisitUpdate


def _visit_options():
    return (selectinload(Visit.items), selectinload(Visit.payment))


def get_visit(db: Session, practice_id: UUID, visit_id: UUID) -> Visit:
    visit = db.scalar(
        select(Visit)
        .where(Visit.id == visit_id, Visit.practice_id == practice_id)
        .options(*_visit_options())
        .execution_options(populate_existing=True)
    )
    if visit is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Visit not found")
    return visit


def visit_total(visit: Visit) -> Decimal:
    return quantize_money(sum((item.subtotal for item in visit.items), Decimal("0.00")))


def serialize_visit(visit: Visit) -> VisitRead:
    total = visit_total(visit)
    paid = quantize_money(visit.payment.amount) if visit.payment is not None else Decimal("0.00")
    return VisitRead(
        id=visit.id,
        practice_id=visit.practice_id,
        pet_id=visit.pet_id,
        user_id=visit.user_id,
        visit_date=visit.visit_date,
        diagnosis=visit.diagnosis,
        notes=visit.notes,
        follow_up_date=visit.follow_up_date,
        items=[VisitItemRead.model_validate(item) for item in visit.items],
        total=total,
        outstanding=quantize_money(total - paid),
        payment=PaymentRead.model_validate(visit.payment) if visit.payment is not None else None,
        created_at=visit.created_at,
        updated_at=visit.updated_at,
    )


def _build_item(db: Session, practice_id: UUID, payload: VisitItemCreate, position: int) -> VisitItem:
    service_id = payload.service_id
    if service_id is not None:
        service = db.scalar(
            select(Service).where(Service.id == service_id, Service.practice_id == practice_id)
        )
        if service is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")
        if not service.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Service is not active")
        unit_price = quantize_money(service.price)
        description = payload.description or service.name
    else:
        unit_price = quantize_money(payload.unit_price)
        description = payload.description or ""
    description = description.strip()
    if not description:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Item description is required")
    return VisitItem(
        service_id=service_id,
        description=description,
        quantity=payload.quantity,
        unit_price=unit_price,
        subtotal=quantize_money(unit_price * payload.quantity),
        position=position,
    )


def _replace_items(db: Session, visit: Visit, practice_id: UUID, items: list[VisitItemCreate]) -> None:
    visit.items.clear()
    db.flush()
    for position, item in enumerate(items):
        visit.items.append(_build_item(db, practice_id, item, position))
    db.flush()
    if visit.payment is not None and visit.payment.amount > visit_total(visit):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Visit total would be less than the recorded payment",
        )


def _require_pet(db: Session, practice_id: UUID, pet_id: UUID) -> Pet:
    return get_owned(db, Pet, pet_id, practice_id, "Pet not found")


def create_visit(db: Session, user: User, payload: VisitCreate) -> VisitRead:
    _require_pet(db, user.practice_id, payload.pet_id)
    visit = Visit(
        practice_id=user.practice_id,
        pet_id=payload.pet_id,
        user_id=user.id,
        visit_date=payload.visit_date,
        diagnosis=payload.diagnosis,
        notes=payload.notes,
        follow_up_date=payload.follow_up_date,
    )
    for position, item in enumerate(payload.items):
        visit.items.append(_build_item(db, user.practice_id, item, position))
    db.add(visit)
    db.commit()
    return serialize_visit(get_visit(db, user.practice_id, visit.id))


def update_visit(db: Session, user: User, visit_id: UUID, payload: VisitUpdate) -> VisitRead:
    visit = get_visit(db, user.practice_id, visit_id)
    changes = payload.model_dump(exclude_unset=True)
    items = changes.pop("items", None)
    if "pet_id" in changes and changes["pet_id"] is not None:
        _require_pet(db, user.practice_id, changes["pet_id"])
    for key, value in changes.items():
        setattr(visit, key, value)
    if items is not None:
        _replace_items(db, visit, user.practice_id, payload.items or [])
    visit.updated_at = datetime.now(timezone.utc)
    db.commit()
    return serialize_visit(get_visit(db, user.practice_id, visit.id))


def delete_visit(db: Session, user: User, visit_id: UUID) -> None:
    visit = get_visit(db, user.practice_id, visit_id)
    db.delete(visit)
    db.commit()


def list_visits(db: Session, practice_id: UUID, pet_id: UUID | None = None) -> list[VisitRead]:
    statement = (
        select(Visit)
        .where(Visit.practice_id == practice_id)
        .options(*_visit_options())
        .execution_options(populate_existing=True)
        .order_by(Visit.visit_date.desc(), Visit.created_at.desc())
    )
    if pet_id is not None:
        _require_pet(db, practice_id, pet_id)
        statement = statement.where(Visit.pet_id == pet_id)
    return [serialize_visit(visit) for visit in db.scalars(statement).all()]


def record_payment(db: Session, user: User, payload: PaymentCreate) -> Payment:
    visit = get_visit(db, user.practice_id, payload.visit_id)
    existing = db.scalar(select(Payment.id).where(Payment.visit_id == visit.id))
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This visit already has a payment",
        )
    total = visit_total(visit)
    if payload.amount > total:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment amount cannot exceed the visit total",
        )
    paid_at = payload.paid_at or datetime.now(timezone.utc)
    if paid_at.tzinfo is None:
        paid_at = paid_at.replace(tzinfo=timezone.utc)
    payment = Payment(
        practice_id=user.practice_id,
        visit_id=visit.id,
        amount=payload.amount,
        payment_method=payload.payment_method,
        paid_at=paid_at,
    )
    visit.payment = payment
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This visit already has a payment",
        ) from exc
    db.refresh(payment)
    return payment


def payment_for_visit(db: Session, practice_id: UUID, visit_id: UUID) -> Payment:
    get_visit(db, practice_id, visit_id)
    payment = db.scalar(
        select(Payment).where(Payment.visit_id == visit_id, Payment.practice_id == practice_id)
    )
    if payment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    return payment


def list_payments(db: Session, practice_id: UUID) -> list[Payment]:
    statement = (
        select(Payment)
        .where(Payment.practice_id == practice_id)
        .order_by(Payment.paid_at.desc(), Payment.id)
    )
    return list(db.scalars(statement).all())


def _iso(value) -> str | None:
    if value is None:
        return None
    return value.isoformat()


def pet_history(db: Session, practice_id: UUID, pet_id: UUID) -> PetHistory:
    pet = get_owned(db, Pet, pet_id, practice_id, "Pet not found")
    events: list[tuple] = []

    visits = db.scalars(
        select(Visit)
        .where(Visit.practice_id == practice_id, Visit.pet_id == pet.id)
        .options(*_visit_options())
        .execution_options(populate_existing=True)
    ).all()
    for visit in visits:
        serialized = serialize_visit(visit)
        events.append(
            (
                visit.visit_date,
                visit.created_at,
                TimelineEvent(
                    type="visit",
                    date=visit.visit_date,
                    title=visit.diagnosis or "Visit",
                    details={
                        "id": str(visit.id),
                        "diagnosis": visit.diagnosis,
                        "notes": visit.notes,
                        "total": float(serialized.total),
                        "outstanding": float(serialized.outstanding),
                        "items": [item.description for item in visit.items],
                    },
                ),
            )
        )
        if visit.payment is not None:
            paid_at = visit.payment.paid_at
            if paid_at.tzinfo is None:
                paid_at = paid_at.replace(tzinfo=timezone.utc)
            events.append(
                (
                    paid_at.astimezone(timezone.utc).date(),
                    paid_at,
                    TimelineEvent(
                        type="payment",
                        date=paid_at.astimezone(timezone.utc).date(),
                        title="Payment received",
                        details={
                            "id": str(visit.payment.id),
                            "visit_id": str(visit.id),
                            "amount": float(visit.payment.amount),
                            "payment_method": visit.payment.payment_method,
                        },
                    ),
                )
            )

    vaccinations = db.scalars(
        select(Vaccination).where(
            Vaccination.practice_id == practice_id,
            Vaccination.pet_id == pet.id,
        )
    ).all()
    for vaccination in vaccinations:
        events.append(
            (
                vaccination.administered_date,
                vaccination.created_at,
                TimelineEvent(
                    type="vaccination",
                    date=vaccination.administered_date,
                    title=vaccination.vaccine_name,
                    details={
                        "id": str(vaccination.id),
                        "vaccine_name": vaccination.vaccine_name,
                        "next_due_date": _iso(vaccination.next_due_date),
                        "batch_number": vaccination.batch_number,
                        "notes": vaccination.notes,
                        "visit_id": str(vaccination.visit_id) if vaccination.visit_id else None,
                    },
                ),
            )
        )

    events.sort(key=lambda item: (item[0], item[1]), reverse=True)
    return PetHistory(pet=PetRead.model_validate(pet), timeline=[item[2] for item in events])

