from fastapi import FastAPI
from app.api.v1.api import api_router
from app.core.config import get_settings
from app.core.database import Base, engine
from fastapi.openapi.utils import get_openapi

# FastAPI 애플리케이션 생성
app = FastAPI(
    title="API",
    description="Python FastAPI",
    version="1.0.0",
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

def custom_openapi():
    schema = get_openapi(title="API", version="1.0.0", routes=app.routes)
    schema.setdefault("components", {}).setdefault("securitySchemes", {})
    schema["components"]["securitySchemes"]["bearerAuth"] = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
    }
    # (선택) 전역 기본 보안
    # schema["security"] = [{SCHEME_NAME: []}]
    app.openapi_schema = schema
    return schema

app.openapi = custom_openapi

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# v1 API 라우터를 메인 앱에 포함
app.include_router(api_router, prefix="/api/v1")

@app.get("/api", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the Janus API Gateway!"}