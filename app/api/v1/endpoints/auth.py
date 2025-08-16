from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Response, Cookie, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.config import get_settings
from app.schemas.user import UserCreate
from app.schemas.auth import LoginIn, TokenOut
from app.services.auth_service import (
    register_user,
    login_issue_tokens,
    rotate_refresh,
    revoke_refresh,
)

router = APIRouter()
_settings = get_settings()

def set_refresh_cookie(response: Response, value: str, max_age: int) -> None:
    response.set_cookie(
        key="refresh_token",
        value=value,
        httponly=True,
        secure=_settings.COOKIE_SECURE,
        samesite=_settings.COOKIE_SAMESITE,
        max_age=max_age,
        path="/",
    )

@router.post("/register", status_code=201)
async def register(body: UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        await register_user(db, body.user_id, body.user_name, body.user_pwd, body.user_number, body.user_gender)
        return {"ok": True}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@router.post("/login", response_model=TokenOut)
async def login(body: LoginIn, request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    try:
        access, expires_in, refresh_plain, refresh_max_age = await login_issue_tokens(
            db=db,
            user_id=body.user_id,
            password=body.user_pwd,
            user_agent=request.headers.get("user-agent"),
            ip=request.client.host if request.client else None,
        )
        set_refresh_cookie(response, refresh_plain, refresh_max_age)
        return TokenOut(access_token=access, expires_in=expires_in)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

@router.post("/refresh", response_model=TokenOut)
async def refresh(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
    refresh_cookie: Optional[str] = Cookie(default=None, alias="refresh_token"),
):
    if not refresh_cookie:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No refresh token")
    try:
        access, expires_in, new_refresh, refresh_max_age = await rotate_refresh(
            db=db,
            refresh_plain=refresh_cookie,
            user_agent=request.headers.get("user-agent"),
            ip=request.client.host if request.client else None,
        )
        set_refresh_cookie(response, new_refresh, refresh_max_age)
        return TokenOut(access_token=access, expires_in=expires_in)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

@router.post("/logout")
async def logout(
    response: Response,
    db: AsyncSession = Depends(get_db),
    refresh_cookie: Optional[str] = Cookie(default=None, alias="refresh_token"),
):
    if refresh_cookie:
        await revoke_refresh(db, refresh_cookie)
    response.delete_cookie("refresh_token", path="/")
    return {"ok": True}
