from fastapi import FastAPI
from app.api.v1.api import api_router
from app.core.config import settings

# FastAPI 애플리케이션 생성
app = FastAPI(
    title="Janus API Gateway",
    description="Python FastAPI를 이용한 Janus 서버 연동 API",
    version="1.0.0",
    docs_url="/docs",
)

# v1 API 라우터를 메인 앱에 포함
app.include_router(api_router, prefix="/v1")

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the Janus API Gateway!"}