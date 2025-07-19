from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.user import User
from app.schemas.user import UserCreate

def create_user(db: Session, user: UserCreate) -> User:
  """새로운 유저를 생성합니다."""

  db_user = User(user_id=user.user_id, user_name=user.user_name)
  db.add(db_user)
  db.commit()
  db.refresh(db_user)
  return db_user