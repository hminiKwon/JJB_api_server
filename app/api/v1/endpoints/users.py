# app/api/v1/endpoints/items.py
from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.schemas.user import User
from app.services import user_service

router = APIRouter()

@router.get("/me")
async def me(user: User = Depends(get_current_user)):
    return {"id": user.id, "email": user.email}