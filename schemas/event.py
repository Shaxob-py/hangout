from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, ConfigDict

class EventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str
    location: str
    date_event: datetime
    max_users: int
    is_active: bool
    owner_id: UUID
    participants_count: int = 0




class EventListResponse(BaseModel):
    items: list[EventOut]
    next_cursor: Optional[str] = None
    has_next: bool


class EventCreateSchema(BaseModel):
    name: str = Field(max_length=100)
    description: str = Field(max_length=255, min_length=10)
    max_users: int = Field(gt=1, le=50)
    location: str = Field(max_length=100)
    date_event: datetime

    @classmethod
    @field_validator("date_event")
    def parse_custom_datetime(cls, value: str | datetime) -> datetime:
        if isinstance(value, datetime):
            return value

        try:
            return datetime.strptime(value, "%Y-%m-%d %H:%M")
        except ValueError:
            raise ValueError("Format must be YYYY-MM-DD HH:MM")

    model_config = ConfigDict(from_attributes=True)


class EventDetailSchema(EventCreateSchema):
    joined_users: int
    is_active: bool
    owner_username:str


class EventUpdateSchema(BaseModel):
    name: str | None = None
    description: str | None = None
    max_users: int | None = None
    location: str | None = None
    date_event: datetime | None = None
    is_active: bool | None = None
