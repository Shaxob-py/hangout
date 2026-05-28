import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from aiogram import Bot
from admin import admin
from database.base import db
from my_bot.main import dp
from root.config import settings
from router import router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await db.create_all()
    admin.mount_to(app)
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)

    bot_task = asyncio.create_task(dp.start_polling(bot))
    print('Project ishga tushdi ')
    yield
    print('Project toxtadi ')


app = FastAPI(
    title="User Service API",
    description="For Effective Mobile",
    version="0.1.0",
    docs_url="/",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

@app.get("/health")
async def health():
    return {"status": "ok"}

app.add_middleware(SessionMiddleware, secret_key=settings.SESSIONMIDDLEWARE)
app.include_router(router, prefix="/api/v1")
