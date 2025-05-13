from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from db import Base
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    components = relationship("Component", back_populates="owner")
    requests = relationship("AIRequestChat", back_populates="user")


class Component(Base):
    __tablename__ = "components"

    id = Column(Integer, primary_key=True, index=True)
    userid = Column(String, ForeignKey("users.id"))
    part = Column(String, unique=False, index=True)
    price = Column(Integer, unique=False, index=True)
    type = Column(String, unique=False, index=True)
    article_number = Column(Integer, unique=True, index=True)

    owner = relationship("User", back_populates="components")


class AIRequestChat(Base):
    __tablename__ = "ai_requests"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    request_text = Column(Text)
    response_text = Column(Text)
    created_at = Column(DateTime, default=datetime.now)

    user = relationship("User", back_populates="requests")
