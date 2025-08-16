import secrets, hashlib
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from jose import jwt
from passlib.context import CryptContext

from app.core.config import get_settings

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(p: str) -> str:
    return pwd_ctx.hash(p)

def verify_password(p: str, hp: str) -> bool:
    return pwd_ctx.verify(p, hp)

def utcnow_naive() -> datetime:
    # DB에 naive UTC로 저장
    return datetime.now()

def make_access_token(sub: str, extra: Optional[Dict[str, Any]] = None) -> str:
    s = get_settings()
    payload: Dict[str, Any] = {
        "sub": sub,
        "typ": "access",
        "iat": int(datetime.now().timestamp()),
        "exp": datetime.now() + timedelta(minutes=s.ACCESS_EXPIRE_MINUTES),
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, s.JWT_SECRET, algorithm=s.JWT_ALG)

def decode_access_token(token: str) -> Dict[str, Any]:
    s = get_settings()
    return jwt.decode(token, s.JWT_SECRET, algorithms=[s.JWT_ALG])

def new_refresh_plain() -> str:
    return secrets.token_urlsafe(32)

def new_jti() -> str:
    return secrets.token_hex(16)  # 32 chars

def hash_refresh(plain: str) -> str:
    s = get_settings()
    h = hashlib.sha256()
    h.update((plain + s.REFRESH_HASH_PEPPER).encode("utf-8"))
    return h.hexdigest()
