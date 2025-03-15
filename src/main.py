from contextlib import asynccontextmanager
from typing import AsyncGenerator

import sentry_sdk

from fastapi import FastAPI, Depends
from redis.asyncio import Redis
from sqlalchemy import text
from starlette.middleware.cors import CORSMiddleware
from starsessions import CookieStore, SessionMiddleware, SessionAutoloadMiddleware
from starsessions.stores.redis import RedisStore

from src.config import app_configs, settings
from src.models import create_tables, get_session
from src.routers.auth import auth_router

redis = Redis.from_url(settings.REDIS_URL)
session_store = RedisStore(connection=redis, prefix="ds_session")


@asynccontextmanager
async def lifespan(_application: FastAPI) -> AsyncGenerator:
    # Startup
    await create_tables()
    yield
    # Shutdown
    await redis.close()


app = FastAPI(**app_configs, lifespan=lifespan)

app.add_middleware(SessionAutoloadMiddleware)
app.add_middleware(SessionMiddleware, store=session_store)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=settings.CORS_ORIGINS_REGEX,
    allow_credentials=True,
    allow_methods=("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"),
    allow_headers=settings.CORS_HEADERS,
)

if settings.ENVIRONMENT.is_deployed:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
    )

app.include_router(auth_router)


@app.get("/")
async def welcome() -> str:
    return "Welcome to the DevSheets API!"


@app.get("/healthcheck", include_in_schema=False)
async def healthcheck(session=Depends(get_session)) -> dict[str, str]:
    db_test = await session.execute(text("SELECT * FROM information_schema.tables"))

    return {"status": "ok", "database": str(db_test.first())}
