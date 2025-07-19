from sqlalchemy import Column, Integer, String
from app.core.database import Base

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True, autoincrement="auto")
    user_id = Column(String(255), index=True)
    user_name = Column(String(255), index=True)
