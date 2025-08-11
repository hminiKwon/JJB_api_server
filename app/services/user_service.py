from sqlalchemy import select
from sqlalchemy.orm import Session, load_only
from typing import List, Optional

from app.models import User
from app.schemas.user import UserCreate

def create_user(db: Session, user: UserCreate) -> User:
  """새로운 유저를 생성합니다."""

  db_user = User(user_id=user.user_id, user_name=user.user_name, user_pwd=user.user_pwd, user_number=user.user_number)
  db.add(db_user)
  db.commit()
  db.refresh(db_user)
  return db_user

def search_user(db: Session, user: User) -> User:
  """유저를 조회합니다."""

  query = select(User).filter_by(user_id=user.user_id).options(
    load_only(User.user_id, User.user_name, User.couple_id)
  )

  target_user = db.execute(query).scalars().first()

  return target_user

