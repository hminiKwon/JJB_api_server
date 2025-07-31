# app/api/v1/endpoints/items.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.user import User, UserCreate
from app.services import user_service

router = APIRouter()

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED, summary="User 생성")
def create_new_item(item: UserCreate, db: Session = Depends(get_db)):
    """새로운 항목을 생성합니다."""
    return user_service.create_item(db=db, item=item)