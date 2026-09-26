import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Practice(Base):
    __tablename__ = "practices"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(50))
    address: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    users: Mapped[list["User"]] = relationship(back_populates="practice")
    owners: Mapped[list["Owner"]] = relationship(back_populates="practice")
    pets: Mapped[list["Pet"]] = relationship(back_populates="practice")
    services: Mapped[list["Service"]] = relationship(back_populates="practice")
    visits: Mapped[list["Visit"]] = relationship(back_populates="practice")
    vaccinations: Mapped[list["Vaccination"]] = relationship(back_populates="practice")
    payments: Mapped[list["Payment"]] = relationship(back_populates="practice")
