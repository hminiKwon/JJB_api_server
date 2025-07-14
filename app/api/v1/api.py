from fastapi import APIRouter
from app.api.v1.endpoints import janus

# API v1 메인 라우터
api_router = APIRouter()

# janus 엔드포인트 라우터를 포함
api_router.include_router(janus.router, prefix="/janus", tags=["Janus VideoRoom"])

# 여기에 다른 엔드포인트 라우터들(users, auth 등)을 추가할 수 있습니다.
# api_router.include_router(users.router, prefix="/users", tags=["Users"])