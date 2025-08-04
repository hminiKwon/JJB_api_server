from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True, autoincrement="auto")
    user_id = Column(String(255), index=True)
    user_name = Column(String(255), index=True)
    couple_id = Column(Integer, ForeignKey("couple.id"))

    couple = relationship("Couple", back_populates="couple")

    def __repr__(self):
        return f"<User(id={self.id}, user_id='{self.user_id}', user_name='{self.user_name}', couple_id={self.couple_id})>"

