import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.owner import Owner
    from app.models.practice import Practice
    from app.models.vaccination import Vaccination
    from app.models.visit import Visit


class Pet(TimestampMixin, Base):
    __tablename__ = "pets"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    practice_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("practices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("owners.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    species: Mapped[str] = mapped_column(String(100), nullable=False)
    breed: Mapped[str | None] = mapped_column(String(100))
    sex: Mapped[str | None] = mapped_column(String(20))
    date_of_birth: Mapped[date | None] = mapped_column(Date)
    color: Mapped[str | None] = mapped_column(String(50))
    notes: Mapped[str | None] = mapped_column(Text)

    practice: Mapped["Practice"] = relationship(back_populates="pets")
    owner: Mapped["Owner"] = relationship(back_populates="pets")
    visits: Mapped[list["Visit"]] = relationship(back_populates="pet")
    vaccinations: Mapped[list["Vaccination"]] = relationship(back_populates="pet")
