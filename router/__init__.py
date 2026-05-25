from fastapi import APIRouter

from router.auth import auth_router
from router.event import event_router

router = APIRouter()

router.include_router(auth_router)
router.include_router(event_router)