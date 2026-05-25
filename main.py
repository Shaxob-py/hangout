from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from database.base import db
from router import router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await db.create_all()
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





app.include_router(router, prefix="/api/v1")
