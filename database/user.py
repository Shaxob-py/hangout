from enum import Enum

from passlib.context import CryptContext
from sqlalchemy import String, BigInteger, select, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import CreatedModel, EventParticipant
from database.base import db

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


class User(CreatedModel):
    class Role(Enum):
        ADMIN = 'ADMIN'
        USER = 'USER'

    username: Mapped[str] = mapped_column(String(50))

    role: Mapped[Role] = mapped_column(
        SQLEnum(Role, name="role"),
        default=Role.USER,

    )
    phone: Mapped[str] = mapped_column(String(15), unique=True)
    telegram_id: Mapped[str] = mapped_column(BigInteger)
    password: Mapped[str] = mapped_column(String(200), nullable=True)

    participants: Mapped[list["EventParticipant"]] = relationship("EventParticipant", back_populates="user")

    @classmethod
    async def get_by_phone(cls, phone: str) -> str:
        query = select(cls).where(cls.phone == phone)

        return (await db.execute(query)).scalar()

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)
