import uuid
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    Date,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.payment import Payment
    from app.models.pet import Pet
    from app.models.practice import Practice
    from app.models.service import Service
    from app.models.user import User
    from app.models.vaccination import Vaccination


class Visit(TimestampMixin, Base):
    __tablename__ = "visits"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    practice_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("practices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    pet_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("pets.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    visit_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    diagnosis: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)
    follow_up_date: Mapped[date | None] = mapped_column(Date)

    practice: Mapped["Practice"] = relationship(back_populates="visits")
    pet: Mapped["Pet"] = relationship(back_populates="visits")
    veterinarian: Mapped["User"] = relationship(back_populates="visits")
    items: Mapped[list["VisitItem"]] = relationship(
        back_populates="visit",
        cascade="all, delete-orphan",
        order_by="VisitItem.position",
    )
    vaccinations: Mapped[list["Vaccination"]] = relationship(
        back_populates="visit",
        passive_deletes=True,
    )
    payment: Mapped["Payment | None"] = relationship(
        back_populates="visit",
        cascade="all, delete-orphan",
        uselist=False,
    )


class VisitItem(Base):
    """Line item with a price copied from the catalog at the time of the visit."""

    __tablename__ = "visit_items"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_visit_items_quantity_positive"),
        CheckConstraint("unit_price >= 0", name="ck_visit_items_unit_price_non_negative"),
        CheckConstraint("subtotal >= 0", name="ck_visit_items_subtotal_non_negative"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    visit_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("visits.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    service_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("services.id", ondelete="SET NULL"),
        index=True,
    )
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    visit: Mapped[Visit] = relationship(back_populates="items")
    service: Mapped["Service | None"] = relationship(back_populates="visit_items")
