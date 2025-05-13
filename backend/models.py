from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    components = relationship("Component", back_populates="owner")
    chat_history = relationship("AIChatHistory", back_populates="user")


class Component(Base):
    __tablename__ = "components"

    id = Column(Integer, primary_key=True, index=True)
    userid = Column(String, ForeignKey("users.id"))
    part = Column(String, unique=False, index=True)
    price = Column(Integer, unique=False, index=True)
    type = Column(String, unique=False, index=True)
    article_number = Column(Integer, unique=True, index=True)

    owner = relationship("User", back_populates="components")


class AIChatHistory(Base):
    __tablename__ = "ai_chat_history"

    id = Column(Integer, primary_key=True, index=True)
    prompt = Column(String, index=True) 
    response = Column(String, index=True) 
    timestamp = Column(String, index=True)
    
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="chat_history")
