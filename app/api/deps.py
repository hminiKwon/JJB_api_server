from typing import Optional
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import APIKeyCookie, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User

# 문서용 토큰 발급 경로는 v1 기준으로 맞춤
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
bearer_scheme = HTTPBearer(auto_error=False, scheme_name="bearerAuth")
refresh_cookie = APIKeyCookie(name="refresh_token", auto_error=False)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    cred_exc = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if credentials is None or (credentials.scheme or "").lower() != "bearer":
        print("No credentials provided or not a bearer token")
        raise cred_exc

    token_str = credentials.credentials
    try:
        payload = decode_access_token(token_str)
        if payload.get("typ") != "access":
            raise cred_exc
        sub = payload.get("sub")
        if not sub:
            raise cred_exc
    except Exception:
        raise cred_exc

    res = await db.execute(select(User).where(User.id == sub))  # 필요시 int(sub)
    user = res.scalar_one_or_none()
    if not user or not user.is_active:
        raise cred_exc
    return user

# (선택) 관리자 권한 가드 예시
# async def require_admin(user: User = Depends(get_current_user)) -> User:
#     # roles가 있다면 검사하는 형태로 확장
#     # if "admin" not in user.roles: raise HTTPException(403, "Forbidden")
#     return user
