import uuid
from datetime import timedelta, datetime, UTC
from typing import Annotated
from fastapi import HTTPException
from fastapi.security import HTTPBearer
from jose import jwt , exceptions
from starlette import status
from fastapi.params import Depends
from database import User
from root.config import settings


http_bearer = HTTPBearer()

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRES)
    to_encode.update({
        "exp": expire,
        "token_type": "access_token",
    })
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=settings.JWT_REFRESH_TOKEN_EXPIRES)
    to_encode.update({
        "exp": expire,
        "token_type": "refresh_token"
    })
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def verify_refresh_token(token: str):
    payload = jwt.decode(token,settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    user_id : str = payload.get('sub')
    token_type : str = payload.get('token_type')
    if not user_id or token_type != 'refresh_token':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Invalid refresh token')
    return uuid.UUID(user_id)


async def get_current_user(token: Annotated[str, Depends(http_bearer)]) -> User:
    token = token.credentials # noqa
    try:
        encoded_jwt = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
    except exceptions.JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    user_id = encoded_jwt.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    try:
        user_id = uuid.UUID(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    user = await User.get(user_id)
    if user:
        return user

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

