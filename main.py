import asyncio
from contextlib import asynccontextmanager

from aiogram import Bot
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from admin import admin
from database import User
from database.base import db
from my_bot.main import dp
from root.config import settings
from router import router
from utils.utils import get_password_hash


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await db.create_all()
    user = await User.get_by_phone(settings.ADMIN_PHONE)
    if user is None:
        await User.create(
            username="admin",
            password=get_password_hash(settings.ADMIN_PASSWORD),
            phone=settings.ADMIN_PHONE,
            role=User.Role.ADMIN,
            telegram_id=settings.ADMIN_TELEGRAM_ID,
        )
    elif user.role == User.Role.ADMIN and (
        not user.password or not user.password.startswith("$argon2")
    ):
        await User.update(
            user.id,
            password=get_password_hash(user.password or settings.ADMIN_PASSWORD),
        )
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)

    bot_task = asyncio.create_task(dp.start_polling(bot))
    print('Project is running ')
    yield
    print("Project stopped")

    bot_task.cancel()
    try:
        await bot_task
    except asyncio.CancelledError:
        pass
    await bot.session.close()


app = FastAPI(
    title="User Service API",
    description="For Effective Mobile",
    version="0.1.0",
    docs_url="/",
    openapi_url="/openapi.json",
    lifespan=lifespan
)
admin.mount_to(app)


@app.get("/health")
async def health():
    return {"status": "ok"}


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key=settings.SESSIONMIDDLEWARE)
app.include_router(router, prefix="/api/v1")
