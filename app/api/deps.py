from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User

# 문서용 토큰 발급 경로는 v1 기준으로 맞춤
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
    )
    try:
        payload = decode_access_token(token)
        if payload.get("typ") != "access":
            raise credentials_exc
        sub = payload.get("sub")
        if not sub:
            raise credentials_exc
    except Exception:
        raise credentials_exc

    res = await db.execute(select(User).where(User.id == int(sub)))
    user = res.scalar_one_or_none()
    if not user or not user.is_active:
        raise credentials_exc
    return user

# (선택) 관리자 권한 가드 예시
# async def require_admin(user: User = Depends(get_current_user)) -> User:
#     # roles가 있다면 검사하는 형태로 확장
#     # if "admin" not in user.roles: raise HTTPException(403, "Forbidden")
#     return user
