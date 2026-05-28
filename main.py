from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from admin import admin
from database.base import db
from root.config import settings
from router import router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await db.create_all()
    admin.mount_to(app)
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
