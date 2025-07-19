from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
  user_id: str
  user_name: str

class UserCreate(UserBase):
  pass

class User(UserBase):
  id: int

  class Config:
    from_attributes = True