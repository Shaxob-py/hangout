import asyncio
from contextlib import asynccontextmanager

from aiogram import Bot
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from admin import admin
from database import User
from database.base import db
from my_bot.main import dp
from root.config import settings
from router import router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await db.create_all()
    user = await User.get_by_phone(settings.ADMIN_PHONE)
    if user is None:
        await User.create(
            username="admin",
            password=settings.ADMIN_PASSWORD,
            phone=settings.ADMIN_PHONE,
            role=User.ROLE_ADMIN,
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


app.add_middleware(SessionMiddleware, secret_key=settings.SESSIONMIDDLEWARE)
app.include_router(router, prefix="/api/v1")
