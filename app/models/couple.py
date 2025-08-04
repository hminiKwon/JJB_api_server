from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base

class Couple(Base):
    __tablename__ = "couple"

    id = Column(Integer, primary_key=True, index=True, autoincrement="auto")

    user = relationship("User", back_populates="user")

    def __repr__(self):
        return f"<Couple(id={self.id})>"