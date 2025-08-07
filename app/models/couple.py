import uuid
from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Couple(Base):
    __tablename__ = "couple"

    id = Column(Integer, primary_key=True, index=True, autoincrement="auto")
    room_pwd = Column(String(255), index=True, default=lambda: str(uuid.uuid4()), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="user")

    # def __repr__(self):
    #     return f"<Couple(id={self.id})>"