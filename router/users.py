from typing import List

from fastapi import APIRouter

user_router = APIRouter(tags=["user"])


# @user_router.get("", response_model)