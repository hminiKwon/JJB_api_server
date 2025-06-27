# app/main.py
from fastapi import FastAPI, Depends, status, Request
import os
import httpx # httpx 모듈 임포트 유지
from dotenv import load_dotenv

load_dotenv()

# 필요한 Janus 관련 모델 및 함수 임포트
from services.janus.api_client import (
    CreateRoomRequest,
    create_videoroom_on_janus,
    list_videorooms_on_janus,
    destroy_videoroom_on_janus,
    get_janus_status_from_admin
)

# lifespan 이벤트를 위한 asynccontextmanager 임포트
from contextlib import asynccontextmanager

# --- 클라이언트가 Janus에 접속할 공용 URL (Nginx 프록시 URL) ---
CLIENT_JANUS_PUBLIC_URL = os.getenv("CLIENT_JANUS_PUBLIC_URL")


# --- Lifespan 이벤트 핸들러 정의 ---
# 이 함수는 FastAPI 앱의 시작과 종료 시점에 호출됩니다.
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI 애플리케이션의 생명 주기를 관리하는 컨텍스트 매니저.
    애플리케이션 시작 시 httpx 클라이언트를 초기화하고, 종료 시 닫습니다.
    """
    # 애플리케이션 시작 시 실행되는 코드
    print("Application startup: Initializing httpx.AsyncClient...")
    app.state.httpx_client = httpx.AsyncClient()
    yield # 여기서 애플리케이션이 실행됩니다.
    # 애플리케이션 종료 시 실행되는 코드 (yield 이후)
    print("Application shutdown: Closing httpx.AsyncClient...")
    if hasattr(app.state, 'httpx_client') and app.state.httpx_client:
        await app.state.httpx_client.aclose()


# --- FastAPI 앱 인스턴스 생성 ---
# lifespan 매개변수에 위에서 정의한 lifespan 함수를 전달합니다.
app = FastAPI(
    title="Janus Management API",
    description="FastAPI backend to manage Janus Gateway VideoRoom plugin.",
    version="1.0.0",
    lifespan=lifespan # 여기에서 lifespan 핸들러를 등록
)


# --- 의존성 주입 함수 ---
# 각 요청에서 app.state에 저장된 httpx 클라이언트 인스턴스를 반환합니다.
async def get_httpx_client_instance(request: Request) -> httpx.AsyncClient:
    """
    애플리케이션 생명주기 동안 유지되는 httpx.AsyncClient 인스턴스를 반환합니다.
    """
    return request.app.state.httpx_client


# --- FastAPI 엔드포인트 정의 ---
# 이 부분은 이전과 동일합니다.

@app.get("/")
async def read_root():
    return {"message": "Welcome to Janus Management API"}

@app.get("/janus/status")
async def get_janus_status(
    client: httpx.AsyncClient = Depends(get_httpx_client_instance)
):
    return await get_janus_status_from_admin(client)

@app.post("/janus/videoroom/create")
async def create_videoroom(
    room_data: CreateRoomRequest,
    client: httpx.AsyncClient = Depends(get_httpx_client_instance)
):
    janus_response = await create_videoroom_on_janus(room_data, client)
    janus_response["janus_api_url"] = CLIENT_JANUS_PUBLIC_URL
    return janus_response

@app.get("/janus/videoroom/list")
async def list_videorooms(
    client: httpx.AsyncClient = Depends(get_httpx_client_instance)
):
    return await list_videorooms_on_janus(client)

@app.delete("/janus/videoroom/destroy/{room_id}")
async def destroy_videoroom(
    room_id: int,
    client: httpx.AsyncClient = Depends(get_httpx_client_instance)
):
    return await destroy_videoroom_on_janus(room_id, client)