from datetime import timedelta
from typing import Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import (
    hash_password,
    verify_password,
    make_access_token,
    new_refresh_plain,
    new_jti,
    hash_refresh,
    utcnow_naive,
)
from app.models.user import User
from app.models.refresh_token import RefreshToken

_settings = get_settings()

# 회원가입
async def register_user(db: AsyncSession, user_id: str, user_name: str, user_pwd: str, user_number: str, user_gender: int) -> None:
    exists = await db.execute(select(User).where(User.user_id == user_id))
    if exists.scalar_one_or_none():
        raise ValueError("ID already registered")
    user = User(user_id=user_id, user_name=user_name, user_pwd=hash_password(user_pwd), user_number=user_number, user_gender=user_gender)
    db.add(user)
    await db.commit()

# 로그인: access, refresh(plain) 발급 및 refresh 저장
async def login_issue_tokens(
    db: AsyncSession,
    user_id: str,
    password: str,
    user_agent: Optional[str],
    ip: Optional[str],
) -> Tuple[str, int, str, int]:
    res = await db.execute(select(User).where(User.user_id == user_id))
    user = res.scalar_one_or_none()
    if not user or not verify_password(password, user.user_pwd):
        raise PermissionError("Invalid id or password")
    if not user.is_active:
        raise PermissionError("User inactive")

    access = make_access_token(str(user.id))
    refresh_plain = new_refresh_plain()

    rt = RefreshToken(
        jti=new_jti(),
        user_id=user.id,
        hashed_token=hash_refresh(refresh_plain),
        user_agent=user_agent,
        ip=ip,
        created_at=utcnow_naive(),
        expires_at=utcnow_naive() + timedelta(days=_settings.REFRESH_EXPIRE_DAYS),
    )
    db.add(rt)
    await db.commit()

    return access, _settings.ACCESS_EXPIRE_MINUTES * 60, refresh_plain, _settings.REFRESH_EXPIRE_DAYS * 24 * 3600

# 리프레시 회전
async def rotate_refresh(
    db: AsyncSession,
    refresh_plain: str,
    user_agent: Optional[str],
    ip: Optional[str],
) -> Tuple[str, int, str, int]:
    hashed = hash_refresh(refresh_plain)

    res = await db.execute(
        select(RefreshToken).where(
            RefreshToken.hashed_token == hashed,
            RefreshToken.revoked_at.is_(None),
            RefreshToken.expires_at > utcnow_naive(),
        )
    )
    current = res.scalar_one_or_none()
    if not current:
        raise PermissionError("Invalid refresh token")

    # revoke old
    current.revoked_at = utcnow_naive()

    # issue new refresh
    new_plain = new_refresh_plain()
    new_rt = RefreshToken(
        jti=new_jti(),
        user_id=current.user_id,
        hashed_token=hash_refresh(new_plain),
        user_agent=user_agent,
        ip=ip,
        created_at=utcnow_naive(),
        expires_at=utcnow_naive() + timedelta(days=_settings.REFRESH_EXPIRE_DAYS),
    )
    db.add(new_rt)
    await db.commit()

    # new access
    access = make_access_token(str(current.user_id))
    return access, _settings.ACCESS_EXPIRE_MINUTES * 60, new_plain, _settings.REFRESH_EXPIRE_DAYS * 24 * 3600

# 로그아웃(리프레시 폐기)
async def revoke_refresh(db: AsyncSession, refresh_plain: str) -> None:
    hashed = hash_refresh(refresh_plain)
    res = await db.execute(
        select(RefreshToken).where(
            RefreshToken.hashed_token == hashed,
            RefreshToken.revoked_at.is_(None),
        )
    )
    rt = res.scalar_one_or_none()
    if rt:
        rt.revoked_at = utcnow_naive()
        await db.commit()
