from typing import Any, AsyncGenerator, AsyncIterator

from asyncio import current_task
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    async_scoped_session,
)
from src.config import settings


DATABASE_URL = str(settings.DATABASE_ASYNC_URL)


class DatabaseSessionManager:
    def __init__(self) -> None:
        self.engine: AsyncSession | None = None
        self.session_maker = None
        self.session = None

    async def init_db(self):
        self.engine = create_async_engine(
            DATABASE_URL,
            echo=True,
            future=True,
            pool_size=settings.DATABASE_POOL_SIZE,
            pool_recycle=settings.DATABASE_POOL_TTL,
            pool_pre_ping=settings.DATABASE_POOL_PRE_PING,
            # connect_args={"check_same_thread": False},
        )

        self.session_maker = async_sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

        self.session = async_scoped_session(self.session_maker, scopefunc=current_task)

    async def close(self):
        if self.engine is None:
            raise Exception("DatabaseSessionManager is not initialized")
        await self.engine.dispose()


sessionmanager = DatabaseSessionManager()


async def get_db() -> AsyncIterator[AsyncSession]:
    session = sessionmanager.session()
    if session is None:
        raise Exception("DatabaseSessionManager is not initialized")
    try:
        yield session
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


# from sqlalchemy import (
#     CursorResult,
#     Insert,
#     MetaData,
#     Select,
#     Update,
#     Column,
#     Integer,
#     String,
# )
# async def fetch_one(
#     select_query: Select | Insert | Update,
#     connection: AsyncConnection | None = None,
#     commit_after: bool = False,
# ) -> dict[str, Any] | None:
#     if not connection:
#         async with engine.connect() as connection:
#             cursor = await _execute_query(select_query, connection, commit_after)
#             return cursor.first()._asdict() if cursor.rowcount > 0 else None

#     cursor = await _execute_query(select_query, connection, commit_after)
#     return cursor.first()._asdict() if cursor.rowcount > 0 else None


# async def fetch_all(
#     select_query: Select | Insert | Update,
#     connection: AsyncConnection | None = None,
#     commit_after: bool = False,
# ) -> list[dict[str, Any]]:
#     if not connection:
#         async with engine.connect() as connection:
#             cursor = await _execute_query(select_query, connection, commit_after)
#             return [r._asdict() for r in cursor.all()]

#     cursor = await _execute_query(select_query, connection, commit_after)
#     return [r._asdict() for r in cursor.all()]


# async def execute(
#     query: Insert | Update,
#     connection: AsyncConnection = None,
#     commit_after: bool = False,
# ) -> None:
#     if not connection:
#         async with engine.connect() as connection:
#             await _execute_query(query, connection, commit_after)
#             return

#     await _execute_query(query, connection, commit_after)


# async def _execute_query(
#     query: Select | Insert | Update,
#     connection: AsyncConnection,
#     commit_after: bool = False,
# ) -> CursorResult:
#     result = await connection.execute(query)
#     if commit_after:
#         await connection.commit()

#     return result
