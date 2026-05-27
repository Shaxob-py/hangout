from pydantic import BaseModel, Field

class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str

class UserLoginSchema(BaseModel):
    phone: str = Field(..., min_length=1, examples=['998901001010'])


class UserVerSchema(BaseModel):
    phone: str = Field(..., min_length=1, examples=['998901001010'])
    code: int = Field(..., examples=['123456'])


class UserCreateSchema(BaseModel):
    username: str
    phone_number: str
    telegram_id: int


class RefreshTokenSchema(BaseModel):
    refresh_token: str