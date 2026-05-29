from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends, Query
from starlette import status
from starlette.status import HTTP_400_BAD_REQUEST

from database import Event, EventParticipant, User
from schemas.base import ResponseWrapper
from schemas.event import (
    EventCreateSchema,
    EventDetailSchema,
    EventOut,
    EventUpdateSchema,
    EventListResponse,
)
from utils.jwt import get_current_user

event_router = APIRouter(tags=["event"])


@event_router.get("/events", response_model=EventListResponse)
async def list_events(
        limit: int = Query(default=20, ge=1, le=50),
        cursor: Optional[str] = Query(default=None),
):
    events, next_cursor = await Event.get_events_page(limit, cursor)

    return EventListResponse(
        items=events,
        next_cursor=next_cursor,
        has_next=next_cursor is not None,
    )


@event_router.post("/event", response_model=ResponseWrapper[EventCreateSchema])
async def create_event_view(data: EventCreateSchema, cur_user=Depends(get_current_user)):
    if await Event.check_limit(cur_user.id):
        await Event.create(name=data.name,
                           description=data.description,
                           max_users=data.max_users,
                           owner_id=cur_user.id,
                           location=data.location,
                           date_event=data.date_event, )

        return ResponseWrapper[EventCreateSchema](
            message=f"Event {data.name} created successfully",
            data=data,
            status_code=status.HTTP_201_CREATED
        )

    raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many requests")


@event_router.get("/event/{event_id}", response_model=ResponseWrapper[EventDetailSchema])
async def detail_event_view(event_id: UUID):
    event = await Event.get(event_id)

    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    user = await User.get(event.owner_id)
    joined_users = await EventParticipant.count_joined_users(event_id)

    event_detail = (
        EventDetailSchema(
            is_active=event.is_active,
            name=event.name,
            description=event.description,
            max_users=event.max_users,
            joined_users=joined_users,
            location=event.location,
            date_event=event.date_event,
            owner_username=user.username
        )
    )
    return ResponseWrapper[EventDetailSchema](
        message=f'Event "{event_id}" was found',
        data=event_detail,
        status_code=status.HTTP_200_OK
    )


@event_router.patch("/event/{event_id}", response_model=ResponseWrapper[EventUpdateSchema])
async def update_event_view(event_id: UUID, data: EventUpdateSchema, cur_user=Depends(get_current_user)):
    event = await Event.get(event_id)

    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    if event.owner_id != cur_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    update_data = data.model_dump(exclude_unset=True)

    await Event.update(event_id, **update_data)

    return ResponseWrapper[EventUpdateSchema](
        message=f'Event "{event_id}" was updated',
        data=data,
        status_code=status.HTTP_200_OK)


@event_router.get("/my_events", response_model=ResponseWrapper[List[EventOut]])
async def get_my_event_view(cur_user=Depends(get_current_user)):
    events = await Event.get_my_events(cur_user.id)

    return ResponseWrapper[List[EventOut]](
        message=f"Found {len(events)} event(s)",
        data=events,
        status_code=status.HTTP_200_OK,
    )


@event_router.delete("/event/{event_id}")
async def delete_event_view(event_id: UUID, cur_user=Depends(get_current_user)):
    event = await Event.get(event_id)

    if event.owner_id != cur_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    await Event.delete(event_id)

    return {
        'status_code': status.HTTP_204_NO_CONTENT}


@event_router.get("/joined_events", response_model=ResponseWrapper[List[EventOut]])
async def get_my_joined_event_view(cur_user=Depends(get_current_user)):
    events = await EventParticipant.get_joined_events(cur_user.id)

    return ResponseWrapper[List[EventOut]](
        message=f"Found {len(events)} joined event(s)",
        data=events,
        status_code=status.HTTP_200_OK,
    )


@event_router.post("/event/join/{event_id}", response_model=ResponseWrapper)
async def join_event_view(event_id: UUID, cur_user=Depends(get_current_user)):
    event_data = await Event.get_events(event_id)

    if event_data.owner_id == cur_user.id:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="You cannot join this event.")

    if event_data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    event, current_count = event_data.Event, event_data.current_count

    if event.is_active is False:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Event is not active")

    if current_count >= event.max_users:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="No more places left")

    event_participant = await EventParticipant.check_events(cur_user.id, event_id)
    if event_participant is None:
        await EventParticipant.create(event_id=event_id, user_id=cur_user.id)
        return ResponseWrapper(
            message=f'EventParticipant "{event_id}" was created',
            data=None,
            status_code=status.HTTP_201_CREATED
        )

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You have event")


@event_router.patch("/event/leave/{event_id}", response_model=ResponseWrapper)
async def leave_event_view(event_id: UUID, cur_user=Depends(get_current_user)):
    event = await EventParticipant.leave_events(cur_user.id, event_id)

    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    return ResponseWrapper(
        message=f'EventParticipant "{event_id}" was changed',
        data=None,
        status_code=status.HTTP_200_OK
    )
