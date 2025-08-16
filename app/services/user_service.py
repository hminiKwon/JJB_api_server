# from sqlalchemy import select
# from sqlalchemy.orm import Session, load_only
# from typing import List, Optional

# from app.models import User
# from app.schemas.user import UserCreate

# def create_user(db: Session, user: UserCreate) -> User:
#   """새로운 유저를 생성합니다."""

#   # Check if a user with the same user_id already exists
#   existing_user = db.query(User).filter_by(user_id=user.user_id).first()
#   if existing_user:
#       raise ValueError("A user with this user_id already exists.")
  
#   # Check if a user with the same user_number already exists
#   existing_number = db.query(User).filter_by(user_number=user.user_number).first()
#   if existing_number:
#       raise ValueError("A user with this user_number already exists.")
  
#   db_user = User(user_id=user.user_id, user_name=user.user_name, user_pwd=user.user_pwd, user_number=user.user_number, user_gender=user.user_gender)
#   db.add(db_user)
#   db.commit()
#   db.refresh(db_user)
#   return db_user

# def search_user(db: Session, user_id: str) -> User:
#   """유저를 조회합니다."""

#   query = select(User).filter_by(user_id=user_id).options(
#     load_only(User.user_id, User.user_name, User.couple_id)
#   )

#   target_user = db.execute(query).scalars().first()

#   return target_user

# def login_user(db: Session, user_id: str, user_pwd: str) -> Optional[User]:
#   """유저 로그인 로직을 처리합니다."""
#   # Find the user by user_id
#   user = db.query(User).filter_by(user_id=user_id).first()
#   if not user:
#     raise ValueError("User not found.")
#   # Check if the provided password matches
#   if user.user_pwd != user_pwd:
#     raise ValueError("Incorrect password.")
#   return user