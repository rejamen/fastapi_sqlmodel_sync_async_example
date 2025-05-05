from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.sync_main import sync_router
from app.async_main import async_router
from app.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(sync_router, tags=["Sync Routes"])
app.include_router(async_router, tags=["Async Routes"])
