from fastapi import APIRouter
from app.api.v1.endpoints import janus, users

# API v1 메인 라우터
api_router = APIRouter()

# janus 엔드포인트 라우터를 포함
api_router.include_router(janus.router, prefix="/janus", tags=["Janus VideoRoom"])
api_router.include_router(users.router, prefix="/users", tags=["users"])