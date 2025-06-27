# app/services/janus/api_client.py
import httpx
import os
from pydantic import BaseModel
from fastapi import HTTPException, status # HTTPException은 FastAPI에서 가져옵니다.

# --- 환경 변수 (이 모듈에서 직접 접근) ---
JANUS_INTERNAL_API_BASE_URL = os.getenv("JANUS_INTERNAL_API_BASE_URL")
JANUS_API_SECRET = os.getenv("JANUS_API_SECRET")
JANUS_ADMIN_API_BASE_URL = os.getenv("JANUS_ADMIN_API_BASE_URL")
JANUS_ADMIN_SECRET = os.getenv("JANUS_ADMIN_SECRET")

# --- Pydantic 모델 정의 ---
# 방 생성 요청 모델
class CreateRoomRequest(BaseModel):
    room_id: int
    description: str = "Default Room"
    is_private: bool = False
    publishers: int = 6
    bitrate: int = 128000
    fir_freq: int = 10
    pin: str | None = None

# 기타 Janus 관련 Pydantic 모델도 여기에 정의할 수 있습니다.
# 예를 들어, 방 참여 요청 모델, 방 정보 응답 모델 등.
class JoinRoomRequest(BaseModel):
    room_id: int
    display_name: str
    role: str = "publisher"

# --- Janus API 호출 함수 ---
async def call_janus_api(
    client: httpx.AsyncClient, # 의존성 주입을 통해 httpx 클라이언트 받기
    plugin: str,
    body: dict,
    admin: bool = False
):
    url = JANUS_INTERNAL_API_BASE_URL
    secret = JANUS_API_SECRET
    transaction_id = os.urandom(8).hex()

    if admin:
        url = JANUS_ADMIN_API_BASE_URL
        secret = JANUS_ADMIN_SECRET
        request_body = {
            "janus": "message",
            "transaction": transaction_id,
            "apisecret": secret,
            **body
        }
    else:
        # 일반 API는 plugin 파라미터와 apisecret을 쿼리 파라미터로 포함
        # Janus 기본 API는 쿼리 파라미터로 secret을 받습니다.
        url = f"{JANUS_INTERNAL_API_BASE_URL}?apisecret={secret}"
        request_body = {
            "janus": "message",
            "body": body,
            "transaction": transaction_id,
            "plugin": f"janus.plugin.{plugin}"
        }

    try:
        response = await client.post(url, json=request_body, timeout=10.0)
        response.raise_for_status()
        janus_response = response.json()

        if janus_response.get("janus") == "error":
            error_data = janus_response.get("error", {})
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Janus API Error: {error_data.get('reason', 'Unknown error')}"
            )
        return janus_response

    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Cannot connect to Janus Gateway: {exc}"
        )
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"Janus API HTTP Error: {exc.response.text}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {e}"
        )

# --- Janus 비디오룸 관련 함수 (call_janus_api를 사용하여 랩핑) ---

async def create_videoroom_on_janus(room_data: CreateRoomRequest, client: httpx.AsyncClient):
    body = {
        "request": "create",
        "room": room_data.room_id,
        "description": room_data.description,
        "is_private": room_data.is_private,
        "publishers": room_data.publishers,
        "bitrate": room_data.bitrate,
        "fir_freq": room_data.fir_freq
    }
    if room_data.pin:
        body["pin"] = room_data.pin

    response = await call_janus_api(client, plugin="videoroom", body=body)

    plugin_data = response.get("plugindata", {}).get("data", {})
    if plugin_data.get("videoroom") == "created":
        return {"message": f"Room {room_data.room_id} created successfully.", "room_id": room_data.room_id}
    elif plugin_data.get("videoroom") == "success" and plugin_data.get("exists"):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Room {room_data.room_id} already exists.")
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create room: {response}")

async def list_videorooms_on_janus(client: httpx.AsyncClient):
    body = {"request": "list"}
    response = await call_janus_api(client, plugin="videoroom", body=body)
    rooms = response.get("plugindata", {}).get("data", {}).get("list", [])
    return {"status": "success", "rooms": rooms}

async def destroy_videoroom_on_janus(room_id: int, client: httpx.AsyncClient):
    body = {"request": "destroy", "room": room_id}
    response = await call_janus_api(client, plugin="videoroom", body=body)
    plugin_data = response.get("plugindata", {}).get("data", {})
    if plugin_data.get("videoroom") == "destroyed":
        return {"message": f"Room {room_id} destroyed successfully."}
    elif plugin_data.get("error"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Room {room_id} not found or error destroying: {plugin_data.get('error')}")
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to destroy room: {response}")

async def get_janus_status_from_admin(client: httpx.AsyncClient):
    body = {"request": "info"}
    response = await call_janus_api(client, plugin="admin", body=body, admin=True)
    return {"status": "success", "data": response}