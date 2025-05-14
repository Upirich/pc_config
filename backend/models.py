from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, JSON
from sqlalchemy.orm import relationship
from db import Base
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    requests = relationship("AIRequestChat", back_populates="user")
    builds = relationship("Build", back_populates="user")


class Component(Base):
    __tablename__ = "components"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=False, index=True)
    price = Column(Integer, unique=False, index=True)
    type = Column(String, unique=False, index=True)
    description = Column(String, unique=False, index=True)


class AIRequestChat(Base):
    __tablename__ = "ai_requests"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    request_text = Column(Text)
    response_text = Column(Text)
    created_at = Column(DateTime, default=datetime.now)

    user = relationship("User", back_populates="requests")


class Build(Base):
    __tablename__ = "builds"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    components = Column(JSON)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="builds")
