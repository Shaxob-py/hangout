from sqlalchemy import String, BigInteger, select
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import CreatedModel, EventParticipant
from database.base import db


class User(CreatedModel):
    username: Mapped[str] = mapped_column(String(50))
    role: Mapped[str] = mapped_column(String, default="user")
    phone: Mapped[str] = mapped_column(String(15), unique=True)
    telegram_id: Mapped[str] = mapped_column(BigInteger)

    participants: Mapped[list["EventParticipant"]] = relationship("EventParticipant", back_populates="user")

    @classmethod
    async def get_by_phone(cls, phone: str) -> str:
        query = select(cls).where(cls.phone == phone)

        return (await db.execute(query)).scalar()
