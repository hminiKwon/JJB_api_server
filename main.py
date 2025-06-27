# app/main.py
from fastapi import FastAPI, Depends, status
import os
# httpx는 이제 app.on_event에서 직접 사용하지 않으므로, 이 파일에서는 임포트가 필수는 아닙니다.
# 하지만 타입 힌트를 위해 남겨두거나, 필요에 따라 제거할 수 있습니다.
import httpx

# 변경된 부분: get_httpx_client 함수를 임포트
from dependencies import get_httpx_client
from services.janus.api_client import (
    CreateRoomRequest,
    create_videoroom_on_janus,
    list_videorooms_on_janus,
    destroy_videoroom_on_janus,
    get_janus_status_from_admin
)

app = FastAPI(
    title="Janus Management API",
    description="FastAPI backend to manage Janus Gateway VideoRoom plugin.",
    version="1.0.0"
)

# --- 클라이언트가 Janus에 접속할 공용 URL (Nginx 프록시 URL) ---
CLIENT_JANUS_PUBLIC_URL = os.getenv("CLIENT_JANUS_PUBLIC_URL")


# --- HTTPX 클라이언트 초기화 및 종료 (app.on_event 부분은 이제 제거합니다) ---
# @app.on_event("startup")
# async def startup_event():
#     app.state.httpx_client = httpx.AsyncClient()

# @app.on_event("shutdown")
# async def shutdown_event():
#     if hasattr(app.state, 'httpx_client') and app.state.httpx_client:
#         await app.state.httpx_client.aclose()


# --- FastAPI 엔드포인트 정의 ---

@app.get("/")
async def read_root():
    return {"message": "Welcome to Janus Management API"}

# Janus Gateway 상태 확인 (Admin API 사용 예시)
@app.get("/janus/status")
async def get_janus_status(
    # 변경된 부분: depends를 통해 get_httpx_client 함수를 컨텍스트 매니저로 사용
    client: httpx.AsyncClient = Depends(get_httpx_client)
):
    return await get_janus_status_from_admin(client)

# 방 생성 API
@app.post("/janus/videoroom/create")
async def create_videoroom(
    room_data: CreateRoomRequest,
    # 변경된 부분: depends를 통해 get_httpx_client 함수를 컨텍스트 매니저로 사용
    client: httpx.AsyncClient = Depends(get_httpx_client)
):
    janus_response = await create_videoroom_on_janus(room_data, client)

    janus_response["janus_api_url"] = CLIENT_JANUS_PUBLIC_URL
    janus_response["janus_websocket_url"] = CLIENT_JANUS_WEBSOCKET_URL
    return janus_response

# 방 목록 조회 API
@app.get("/janus/videoroom/list")
async def list_videorooms(
    # 변경된 부분: depends를 통해 get_httpx_client 함수를 컨텍스트 매니저로 사용
    client: httpx.AsyncClient = Depends(get_httpx_client)
):
    return await list_videorooms_on_janus(client)

# 방 삭제 API
@app.delete("/janus/videoroom/destroy/{room_id}")
async def destroy_videoroom(
    room_id: int,
    # 변경된 부분: depends를 통해 get_httpx_client 함수를 컨텍스트 매니저로 사용
    client: httpx.AsyncClient = Depends(get_httpx_client)
):
    return await destroy_videoroom_on_janus(room_id, client)