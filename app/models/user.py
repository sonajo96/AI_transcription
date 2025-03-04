from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    mobile_phone = Column(String(20), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    password = Column(String(100), nullable=False)

    videos = relationship("Video", back_populates="user", cascade="all, delete")
    chat_history = relationship("ChatHistory", back_populates="user", cascade="all, delete")