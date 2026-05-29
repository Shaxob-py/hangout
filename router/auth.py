from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from starlette import status

from database.user import User
from schemas.base import ResponseWrapper
from schemas.users import UserLoginSchema, UserVerSchema, TokenSchema , RefreshTokenSchema
from services.otp import OTPService, generate_code
from utils.jwt import create_access_token, create_refresh_token, verify_refresh_token

auth_router = APIRouter(prefix="/auth", tags=["auth"])


def otp_service():
    return OTPService()


@auth_router.post("/login", response_model=ResponseWrapper)
async def login_view(data: UserLoginSchema, service: OTPService = Depends(otp_service)):
    user = await User.get_by_phone(data.phone)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Siz bot orqali ro'yxatdan o'tmagansiz. Iltimos, botdan ro'yxatdan o'ting", )

    code = generate_code()
    await service.send_otp(user, code)

    return ResponseWrapper(message='success', data={}, status_code=status.HTTP_200_OK)


@auth_router.post("/verify-code", response_model=ResponseWrapper[TokenSchema])
async def verify_code_view(data: UserVerSchema, service: OTPService = Depends(otp_service)):
    if not await service.verify_otp(data.phone, data.code):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bad request")

    user = await User.get_by_phone(data.phone)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    return ResponseWrapper[TokenSchema](
        message='success',
        data={
            "access_token": access_token,
            "refresh_token": refresh_token
        },
        status_code=status.HTTP_200_OK)




@auth_router.post('/refresh-token')
async def refresh_token(payload: RefreshTokenSchema):  # noqa
    user_uuid = verify_refresh_token(payload.refresh_token)
    new_access_token = create_access_token({'sub': str(user_uuid)})
    return {
        "access_token": new_access_token,
    }