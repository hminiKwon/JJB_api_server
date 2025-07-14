# app/api/v1/endpoints/janus.py

from fastapi import APIRouter, Depends, status, Response
from typing import List

from app.schemas.janus import (
    RoomCreateRequest, RoomDetailsResponse, RoomUpdateRequest,
    ParticipantDetails, SuccessResponse, RoomDestroyRequest
)
from app.services.janus_service import JanusService, janus_service

router = APIRouter()

# CREATE
@router.post(
    "/rooms",
    response_model=RoomDetailsResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Janus 비디오룸 생성"
)
async def create_janus_room(
    request: RoomCreateRequest,
    service: JanusService = Depends(lambda: janus_service)
):
    room_data = await service.create_videoroom(
        description=request.room_description, secret=request.secret
    )
    return RoomDetailsResponse(**room_data)

# READ (List)
@router.get(
    "/rooms",
    response_model=List[RoomDetailsResponse],
    summary="모든 비디오룸 목록 조회"
)
async def get_all_rooms(service: JanusService = Depends(lambda: janus_service)):
    return await service.get_room_list()

# READ (Participants)
@router.get(
    "/rooms/{room_id}/participants",
    response_model=List[ParticipantDetails],
    summary="특정 방의 참여자 목록 조회"
)
async def get_room_participants(
    room_id: int, service: JanusService = Depends(lambda: janus_service)
):
    return await service.get_room_participants(room_id=room_id)

# UPDATE
@router.patch(
    "/rooms/{room_id}",
    response_model=SuccessResponse,
    summary="비디오룸 정보 수정"
)
async def update_room(
    room_id: int,
    request: RoomUpdateRequest,
    service: JanusService = Depends(lambda: janus_service)
):
    await service.edit_videoroom(room_id=room_id, update_data=request)
    return SuccessResponse()

# DELETE
@router.delete(
    "/rooms/{room_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="비디오룸 삭제"
)
async def delete_room(
    room_id: int,
    request: RoomDestroyRequest,
    service: JanusService = Depends(lambda: janus_service)
):
    await service.destroy_videoroom(room_id=room_id, secret=request.secret)
    return Response(status_code=status.HTTP_204_NO_CONTENT)