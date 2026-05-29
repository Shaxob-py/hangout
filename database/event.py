from datetime import datetime, UTC
from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import String, ForeignKey, Integer, select, Boolean, DateTime, func, update
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import CreatedModel
from database.base import db


class Event(CreatedModel):
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(255))
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    max_users: Mapped[int] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    location: Mapped[str] = mapped_column(String(140), )
    date_event: Mapped[datetime] = mapped_column(DateTime)

    participants: Mapped[list["EventParticipant"]] = relationship("EventParticipant", back_populates="event")

    @classmethod
    async def get_events_page(
            cls,
            limit: int = 20,
            cursor: Optional[str] = None,
    ) -> tuple[list['Event'], Optional[str]]:

        stmt = (
            select(Event)
            .where(Event.is_active == True)
            .order_by(Event.date_event.asc(), Event.id.asc())
        )

        if cursor:
            try:
                cursor_id = UUID(cursor)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid cursor")

            cursor_stmt = select(Event.date_event).where(Event.id == cursor_id)
            cursor_date = await db.scalar(cursor_stmt)

            if not cursor_date:
                raise HTTPException(status_code=400, detail="Invalid cursor")

            stmt = stmt.where(
                (Event.date_event > cursor_date) |
                ((Event.date_event == cursor_date) & (Event.id > cursor_id))
            )

        stmt = stmt.limit(limit + 1)
        result = await db.execute(stmt)
        events = list(result.scalars().all())

        has_next = len(events) > limit
        if has_next:
            events = events[:limit]

        next_cursor = str(events[-1].id) if has_next and events else None
        return events, next_cursor

    @classmethod
    async def check_limit(cls, user_id: UUID) -> bool:
        today = datetime.now(UTC).date()
        query = (select(cls)).where(cls.owner_id == user_id, cls.created_at >= today)

        res = await db.execute(query)

        row = res.scalars().all()
        print(len(row))
        return len(row) <= 3

    @classmethod
    async def get_my_events(cls, user_id: UUID) -> List["Event"]:
        query = select(cls).where(cls.owner_id == user_id, cls.is_active.is_(True))
        result = await db.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_events(cls, event_id: UUID):
        query = (
            select(
                cls,
                func.count(EventParticipant.id).filter(EventParticipant.is_active == True).label("current_count")
            )
            .outerjoin(EventParticipant, Event.id == EventParticipant.event_id)
            .where(Event.id == event_id)
            .group_by(Event.id)
        )

        result = await db.execute(query)
        return result.first()


class EventParticipant(CreatedModel):
    event_id: Mapped[int] = mapped_column(
        ForeignKey("events.id")
    )
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))

    user: Mapped[str] = relationship("User", back_populates="participants")
    event: Mapped[str] = relationship("Event", back_populates="participants")
    joined: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    @classmethod
    async def get_joined_events(cls, user_id: UUID) -> List["Event"]:
        query = (
            select(Event)
            .join(cls, cls.event_id == Event.id)
            .where(
                cls.user_id == user_id,
                cls.is_active.is_(True),
                Event.is_active.is_(True),
            )
        )

        result = await db.execute(query)
        return list(result.scalars().all())

    @classmethod
    async def check_events(cls, user_id: UUID, event_id: UUID):
        query = (
            select(cls)
            .where(
                (cls.user_id == user_id) &
                (cls.event_id == event_id) &
                (cls.is_active == True) &
                (func.date(cls.joined) == datetime.now(UTC).date())
            )
        )

        result = await db.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def leave_events(cls, user_id: UUID, event_id: UUID) -> List["Event"]:
        query = (
            update(cls).
            where((cls.user_id == user_id) & (event_id == cls.event_id) & (cls.is_active == True)).values(
                is_active=False).returning(cls))
        result = await db.execute(query)
        await db.commit()
        return result.scalar_one_or_none()

    @classmethod
    async def count_joined_users(cls , event_id) -> int:
        query = (select(cls)).where((cls.is_active == True )&(cls.event_id == event_id))
        result = await db.execute(query)
        return len(result.scalars().all())
