# app/services/janus_service.py

import httpx
import random
import string
import asyncio
from fastapi import HTTPException, status
from app.core.config import get_settings
from app.schemas.janus import RoomUpdateRequest

settings = get_settings()

# ( _generate_transaction_id 함수는 그대로 사용 )
def _generate_transaction_id(length: int = 12) -> str:
    return "".join(random.choice(string.ascii_letters + string.digits) for _ in range(length))


class JanusService:
    def __init__(self):
        self.session_id: int | None = None
        self.handle_id: int | None = None
        self.keepalive_task: asyncio.Task | None = None
        self._lock = asyncio.Lock()

    async def _send_request(self, payload: dict) -> dict:
        # ( 기존 _send_request 함수는 그대로 사용 )
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(settings.JANUS_SERVER_URL, json=payload, timeout=5.0)
                response.raise_for_status()
                janus_response = response.json()
                if janus_response.get("janus") == "error":
                    error = janus_response.get("error", {})
                    raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Janus API Error: {error.get('code')} {error.get('reason')}")
                return janus_response
            except httpx.HTTPStatusError as e:
                raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Failed to communicate with Janus server: {e.response.text}")
            except httpx.RequestError as e:
                raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Could not connect to Janus server: {e}")

    async def _initialize_session(self):
        """세션과 비디오룸 핸들을 한번만 생성하고, self에 저장"""
        async with self._lock:
            if self.session_id and self.handle_id:
                # 이미 초기화된 경우, 바로 리턴
                return

            # 1. Create Session
            session_payload = {"janus": "create", "transaction": _generate_transaction_id()}
            session_response = await self._send_request(session_payload)
            self.session_id = session_response["data"]["id"]
            print(f"✅ Janus Session Created: {self.session_id}")

            # 2. Attach Plugin
            attach_payload = {"janus": "attach", "session_id": self.session_id, "plugin": "janus.plugin.videoroom", "transaction": _generate_transaction_id()}
            attach_response = await self._send_request(attach_payload)
            self.handle_id = attach_response["data"]["id"]
            print(f"✅ Janus Handle Attached: {self.handle_id}")

            # 3. Start Keep-Alive Task (Optional but recommended)
            if self.keepalive_task:
                self.keepalive_task.cancel()
            self.keepalive_task = asyncio.create_task(self._keepalive())

    async def _keepalive(self):
        """세션이 타임아웃되지 않도록 주기적으로 keepalive 메시지를 보냄"""
        while True:
            await asyncio.sleep(30)  # Janus의 세션 타임아웃(기본값 60초)보다 짧게 설정
            try:
                payload = {"janus": "keepalive", "session_id": self.session_id, "transaction": _generate_transaction_id()}
                await self._send_request(payload)
                print(f"🔄 Janus session keepalive sent for session {self.session_id}")
            except Exception as e:
                print(f"❌ Failed to send keepalive, attempting to reconnect: {e}")
                self.session_id = None # 세션 초기화
                self.handle_id = None
                await self._initialize_session() # 재연결 시도

    async def _get_session_and_handle(self) -> (int, int):
        """초기화되지 않았으면 초기화를 실행하고, 저장된 세션/핸들 ID를 반환"""
        if not self.session_id or not self.handle_id:
            await self._initialize_session()
        return self.session_id, self.handle_id

    # CREATE
    async def create_videoroom(self, description: str, secret: str | None = None) -> dict:
        session_id, handle_id = await self._get_session_and_handle()
        create_room_payload = {
            "janus": "message", "session_id": session_id, "handle_id": handle_id, "transaction": _generate_transaction_id(),
            "body": {"request": "create", "description": description, "secret": secret, "is_private": bool(secret), "permanent": True}
        }
        room_response = await self._send_request(create_room_payload)
        plugindata = room_response.get("plugindata", {}).get("data", {})
        if plugindata.get("videoroom") == "created":
            return {"room": plugindata["room"], "description": description, "is_private": bool(secret),"permanent": plugindata.get("permanent", True), "num_participants": 0}
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create room in Janus.")

    # READ (List)
    async def get_room_list(self) -> list:
        session_id, handle_id = await self._get_session_and_handle()
        list_rooms_payload = {
            "janus": "message", "session_id": session_id, "handle_id": handle_id, "transaction": _generate_transaction_id(),
            "body": {"request": "list"}
        }
        response = await self._send_request(list_rooms_payload)
        return response.get("plugindata", {}).get("data", {}).get("list", [])

    # READ (Participants)
    async def get_room_participants(self, room_id: int) -> list:
        session_id, handle_id = await self._get_session_and_handle()
        list_participants_payload = {
            "janus": "message", "session_id": session_id, "handle_id": handle_id, "transaction": _generate_transaction_id(),
            "body": {"request": "listparticipants", "room": room_id}
        }
        response = await self._send_request(list_participants_payload)
        return response.get("plugindata", {}).get("data", {}).get("participants", [])

    # UPDATE
    async def edit_videoroom(self, room_id: int, update_data: RoomUpdateRequest) -> dict:
        session_id, handle_id = await self._get_session_and_handle()
        body = {"request": "edit", "room": room_id}
        body.update(update_data.model_dump(exclude_unset=True)) # 입력된 필드만 추가
        
        edit_room_payload = {
            "janus": "message", "session_id": session_id, "handle_id": handle_id, "transaction": _generate_transaction_id(),
            "body": body
        }
        response = await self._send_request(edit_room_payload)
        plugindata = response.get("plugindata", {}).get("data", {})
        if plugindata.get("videoroom") == "edited":
             return {"room": plugindata["room"]}
        raise HTTPException(status_code=500, detail="Failed to edit room")

    # DELETE
    async def destroy_videoroom(self, room_id: int, secret: str | None = None):
        session_id, handle_id = await self._get_session_and_handle()
        destroy_room_payload = {
            "janus": "message", "session_id": session_id, "handle_id": handle_id, "transaction": _generate_transaction_id(),
            "body": {"request": "destroy", "room": room_id, "secret": secret}
        }
        response = await self._send_request(destroy_room_payload)
        if response.get("plugindata", {}).get("data", {}).get("videoroom") == "destroyed":
            return
        raise HTTPException(status_code=500, detail="Failed to destroy room")


janus_service = JanusService()