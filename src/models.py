from contextlib import asynccontextmanager
from sqlmodel import Field, SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker

from src.config import settings


# Base Models
class UserBase(SQLModel):
    name: str
    email: str = Field(unique=True)


# Models for DB Tables
class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_pw: str


# Models for Clients and API documentation
class UserCreate(UserBase):
    password: str
    pass


class UserSignIn(SQLModel):
    email: str
    password: str


class UserPublic(UserBase):
    id: int


engine = create_async_engine(
    settings.DATABASE_ASYNC_URL.unicode_string(),
    echo=True,
    future=True,
    pool_size=20,
    max_overflow=20,
    pool_recycle=3600,
)


async def get_session() -> AsyncSession:
    async with AsyncSession(engine) as session:
        yield session


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


# async def get_session():
#     async with AsyncSession(engine) as session:
#         yield session
