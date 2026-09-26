"""Development seed for Happy Paws Veterinary Clinic.

Re-running is a no-op when the owner login already exists.
Dev passwords are documented in the repository README and are not for production.
"""

from datetime import datetime, time, timedelta, timezone
from decimal import Decimal

from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.money import quantize_money
from app.core.security import hash_password
from app.models.owner import Owner
from app.models.payment import METHOD_CASH, Payment
from app.models.pet import Pet
from app.models.practice import Practice
from app.models.service import Service
from app.models.user import ROLE_OWNER, ROLE_STAFF, User
from app.models.vaccination import Vaccination
from app.models.visit import Visit, VisitItem
from app.services.analytics import utc_today

OWNER_EMAIL = "sarah@happypaws.example"
STAFF_EMAIL = "assistant@happypaws.example"
OWNER_PASSWORD = "HappyPaws-Sarah-1"
STAFF_PASSWORD = "HappyPaws-Assist-1"


def _at(day) -> datetime:
    return datetime.combine(day, time(12, 0), tzinfo=timezone.utc)


def _add_visit(db, practice, pet, user, day, notes, lines, diagnosis=None) -> Visit:
    visit = Visit(
        practice_id=practice.id,
        pet_id=pet.id,
        user_id=user.id,
        visit_date=day,
        diagnosis=diagnosis,
        notes=notes,
        created_at=_at(day),
        updated_at=_at(day),
    )
    total = Decimal("0.00")
    for position, (service, quantity) in enumerate(lines):
        unit_price = quantize_money(service.price)
        subtotal = quantize_money(unit_price * quantity)
        total += subtotal
        visit.items.append(
            VisitItem(
                service_id=service.id,
                description=service.name,
                quantity=quantity,
                unit_price=unit_price,
                subtotal=subtotal,
                position=position,
            )
        )
    db.add(visit)
    db.flush()
    db.add(
        Payment(
            practice_id=practice.id,
            visit_id=visit.id,
            amount=quantize_money(total),
            payment_method=METHOD_CASH,
            paid_at=_at(day),
        )
    )
    return visit


def seed() -> None:
    db = SessionLocal()
    try:
        existing = db.scalar(select(User).where(User.email == OWNER_EMAIL))
        if existing is not None:
            print("Seed already present; nothing to do.")
            return

        today = utc_today()
        practice = Practice(
            name="Happy Paws Veterinary Clinic",
            phone="555-0148",
            address="12 Clinic Lane",
        )
        db.add(practice)
        db.flush()

        sarah = User(
            practice_id=practice.id,
            name="Dr. Sarah",
            email=OWNER_EMAIL,
            password_hash=hash_password(OWNER_PASSWORD),
            role=ROLE_OWNER,
        )
        assistant = User(
            practice_id=practice.id,
            name="Assistant",
            email=STAFF_EMAIL,
            password_hash=hash_password(STAFF_PASSWORD),
            role=ROLE_STAFF,
        )
        db.add_all([sarah, assistant])

        john = Owner(practice_id=practice.id, name="John", phone="555-0101", email="john@example.com")
        maria = Owner(practice_id=practice.id, name="Maria", phone="555-0102", email="maria@example.com")
        david = Owner(practice_id=practice.id, name="David", phone="555-0103", email="david@example.com")
        db.add_all([john, maria, david])
        db.flush()

        milo = Pet(
            practice_id=practice.id,
            owner_id=john.id,
            name="Milo",
            species="Dog",
            breed="Golden Retriever",
            sex="male",
            color="gold",
            created_at=_at(today - timedelta(days=40)),
            updated_at=_at(today - timedelta(days=40)),
        )
        luna = Pet(
            practice_id=practice.id,
            owner_id=maria.id,
            name="Luna",
            species="Cat",
            breed="Domestic Shorthair",
            sex="female",
            created_at=_at(today - timedelta(days=12)),
            updated_at=_at(today - timedelta(days=12)),
        )
        rocky = Pet(
            practice_id=practice.id,
            owner_id=david.id,
            name="Rocky",
            species="Dog",
            breed="Mixed",
            sex="male",
            created_at=_at(today - timedelta(days=2)),
            updated_at=_at(today - timedelta(days=2)),
        )
        db.add_all([milo, luna, rocky])

        catalog = {
            "Consultation": Service(
                practice_id=practice.id, name="Consultation", price=Decimal("1500.00")
            ),
            "Rabies Vaccination": Service(
                practice_id=practice.id,
                name="Rabies Vaccination",
                price=Decimal("2500.00"),
            ),
            "Deworming": Service(practice_id=practice.id, name="Deworming", price=Decimal("800.00")),
            "Wound Dressing": Service(
                practice_id=practice.id, name="Wound Dressing", price=Decimal("1200.00")
            ),
            "Nail Clipping": Service(
                practice_id=practice.id, name="Nail Clipping", price=Decimal("500.00")
            ),
        }
        db.add_all(catalog.values())
        db.flush()

        milo_visit = _add_visit(
            db,
            practice,
            milo,
            sarah,
            today - timedelta(days=20),
            "Annual exam and deworming",
            [(catalog["Consultation"], 1), (catalog["Deworming"], 1)],
            diagnosis="Healthy",
        )
        luna_visit = _add_visit(
            db,
            practice,
            luna,
            sarah,
            today - timedelta(days=10),
            "Rabies booster",
            [(catalog["Rabies Vaccination"], 1)],
            diagnosis="Vaccinated",
        )
        _add_visit(
            db,
            practice,
            rocky,
            sarah,
            today - timedelta(days=2),
            "Paw laceration",
            [(catalog["Wound Dressing"], 1), (catalog["Nail Clipping"], 1)],
            diagnosis="Laceration",
        )
        _add_visit(
            db,
            practice,
            milo,
            sarah,
            today,
            "Recheck",
            [(catalog["Consultation"], 1)],
            diagnosis="General consultation",
        )

        db.add_all(
            [
                Vaccination(
                    practice_id=practice.id,
                    pet_id=milo.id,
                    visit_id=milo_visit.id,
                    vaccine_name="Rabies",
                    administered_date=today - timedelta(days=20),
                    next_due_date=today + timedelta(days=14),
                    batch_number="RB-2041",
                    created_at=_at(today - timedelta(days=20)),
                ),
                Vaccination(
                    practice_id=practice.id,
                    pet_id=luna.id,
                    visit_id=luna_visit.id,
                    vaccine_name="Rabies",
                    administered_date=today - timedelta(days=10),
                    next_due_date=today + timedelta(days=200),
                    batch_number="RB-2048",
                    created_at=_at(today - timedelta(days=10)),
                ),
                Vaccination(
                    practice_id=practice.id,
                    pet_id=rocky.id,
                    vaccine_name="DHPP",
                    administered_date=today - timedelta(days=2),
                    next_due_date=today + timedelta(days=5),
                    batch_number="DH-118",
                    created_at=_at(today - timedelta(days=2)),
                ),
            ]
        )
        db.commit()
        print("Seeded Happy Paws Veterinary Clinic.")
        print("Dev logins are documented in the README.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
