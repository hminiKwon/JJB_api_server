from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
  user_id: str
  user_name: str

class UserCreate(UserBase):
  user_pwd: str
  user_number: str
  user_gender: int
  pass

class User(UserBase):
  id: int

  class Config:
    from_attributes = True