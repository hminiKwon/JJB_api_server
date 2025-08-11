# app/api/v1/endpoints/items.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.user import User, UserCreate
from app.services import user_service

router = APIRouter()

@router.post("/create", response_model=User, status_code=status.HTTP_201_CREATED, summary="User 생성")
def create_new_user(user: UserCreate, db: Session = Depends(get_db)):
    """새로운 유저를 생성합니다."""
    return user_service.create_user(db=db, user=user)

@router.get("/search", response_model=User, status_code=status.HTTP_200_OK, summary="User 검색")
def search_user(user_id: User.user_id, db:Session = Depends(get_db)):
    """유저를 조회합니다."""

    return user_service.create_user(db=db, user_id=user_id)