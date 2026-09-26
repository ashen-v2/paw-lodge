import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.pet import Pet
    from app.models.practice import Practice
    from app.models.visit import Visit


class Vaccination(Base):
    __tablename__ = "vaccinations"
    __table_args__ = (
        CheckConstraint(
            "next_due_date IS NULL OR next_due_date >= administered_date",
            name="ck_vaccinations_due_not_before_administered",
        ),
    )

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
    visit_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("visits.id", ondelete="SET NULL"),
        index=True,
    )
    vaccine_name: Mapped[str] = mapped_column(String(255), nullable=False)
    administered_date: Mapped[date] = mapped_column(Date, nullable=False)
    next_due_date: Mapped[date | None] = mapped_column(Date, index=True)
    batch_number: Mapped[str | None] = mapped_column(String(100))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    practice: Mapped["Practice"] = relationship(back_populates="vaccinations")
    pet: Mapped["Pet"] = relationship(back_populates="vaccinations")
    visit: Mapped["Visit | None"] = relationship(back_populates="vaccinations")
