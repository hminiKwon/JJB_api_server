from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True, autoincrement="auto", nullable=False)
    user_id = Column(String(255), index=True, nullable=False)
    user_pwd = Column(String(255), index=True, nullable=False)
    user_name = Column(String(255), index=True, nullable=False)
    couple_id = Column(Integer, ForeignKey("couple.id"))
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    couple = relationship("Couple", back_populates="couple")

    # def __repr__(self):
    #     return f"<User(id={self.id}, user_id='{self.user_id}', user_name='{self.user_name}', couple_id={self.couple_id})>"

