from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import Response, RedirectResponse
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import get_session, User, UserCreate, UserPublic, UserSignIn
from src.utils import pwd_context

auth_router = APIRouter()


@auth_router.post(
    "/users",
    responses={
        400: {"description": "User with existing email already exists"},
        401: {"description": "User is already logged in"},
    },
)
async def create_user(
    request: Request, user: UserCreate, session: AsyncSession = Depends(get_session)
) -> UserPublic:
    if request.session.get("user_id") is not None:
        raise HTTPException(401, detail="User is already logged in")

    existing_user = await session.execute(select(User).where(User.email == user.email))
    if existing_user.scalar() is not None:
        raise HTTPException(400, detail="User with that email already exists")

    hash = pwd_context.hash(user.password)
    new_user = User.model_validate(user, update={"hashed_pw": hash})
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    request.session["user_id"] = new_user.id

    return UserPublic.model_validate(new_user)


@auth_router.post("/login")
async def sign_in(
    request: Request, body: UserSignIn, session: AsyncSession = Depends(get_session)
) -> None:
    if request.session.get("user_id") is not None:
        raise HTTPException(401, detail="User is already logged in")

    user = (
        await session.execute(select(User).where(User.email == body.email))
    ).scalar()
    if user is None:
        raise HTTPException(
            400, detail="Login failed, please check your username and password"
        )

    is_match = pwd_context.verify(body.password, user.hashed_pw)
    if not is_match:
        raise HTTPException(
            400, detail="Login failed, please check your username and password"
        )

    request.session["user_id"] = user.id
    return Response(None, 200)


@auth_router.get("/logout")
async def sign_out(request: Request, session: AsyncSession = Depends(get_session)):
    if request.session.get("user_id") is None:
        raise HTTPException(401, detail="User is not logged in")
    request.session.clear()
    return RedirectResponse("/", 302)


@auth_router.get(
    "/whoami", responses={401: {"description": "Current User doesn't exist"}}
)
async def get_current_user(
    request: Request, session: AsyncSession = Depends(get_session)
) -> UserPublic:
    user_id = request.session.get("user_id")
    user = await session.get(User, user_id)
    if user is None:
        raise HTTPException(401, detail="That user could not be found")

    return UserPublic.model_validate(user)
