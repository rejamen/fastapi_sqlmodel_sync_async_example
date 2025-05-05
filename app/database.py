from sqlmodel import create_engine
from sqlalchemy.ext.asyncio import create_async_engine
from app.models import (
    ContactDB, ProductDB,
    OrderDB, OrderLineDB,
    TagDB, OrderTagRelDB
)
from sqlmodel import SQLModel
from app.settings import Settings

settings = Settings()

HOST = settings.DB_HOST
PORT = settings.DB_PORT
DB_NAME = settings.DB_NAME
DB_USER = settings.DB_USER
DB_PASSWORD = settings.DB_PASSWORD
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{HOST}:{PORT}/{DB_NAME}"
ASYNC_DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{HOST}:{PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL, echo=False)
async_engine = create_async_engine(ASYNC_DATABASE_URL, echo=False) 

def init_db():
    SQLModel.metadata.create_all(engine)
