# app/api/v1/endpoints/items.py
from fastapi import APIRouter, Depends, Request

from app.api.deps import get_current_user
from app.schemas.user import User
from app.services import user_service

router = APIRouter()

@router.get("/me")
async def me(request: Request, user: User = Depends(get_current_user)):
    return {"id": user.user_id, "name": user.user_name}

# @router.get("/test")
# async def test(request: Request):
#     print(request.headers.get("authorization"))
#     return {}