# app/schemas/janus.py

from pydantic import BaseModel, Field
from typing import Optional, List

# --- 요청 스키마 ---

class RoomCreateRequest(BaseModel):
    room_description: str = Field(..., description="생성할 방의 설명", example="My Test Room")
    secret: Optional[str] = Field(None, description="방에 접근하기 위한 비밀번호", example="supersecret")

class RoomUpdateRequest(BaseModel):
    new_description: Optional[str] = Field(None, description="변경할 새 방 설명", example="My Updated Room")
    new_secret: Optional[str] = Field(None, description="변경할 새 비밀번호", example="new_supersecret")
    secret: Optional[str] = Field(None, description="수정에 필요한 현재 방 비밀번호")

class RoomDestroyRequest(BaseModel):
    secret: Optional[str] = Field(None, description="방 삭제에 필요한 비밀번호")


# --- 응답 스키마 ---

class RoomDetailsResponse(BaseModel):
    room: int = Field(..., description="방 고유 ID")
    description: str = Field(..., description="방 설명")
    # is_private: bool = Field(..., alias="private", description="비공개 방 여부")
    num_participants: int = Field(..., description="현재 참여자 수")

class ParticipantDetails(BaseModel):
    id: int = Field(..., description="참여자 고유 ID")
    display: str = Field(..., description="참여자 표시 이름")

class SuccessResponse(BaseModel):
    status: str = "success"