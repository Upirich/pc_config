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
    assemblies = relationship("Assembly", back_populates="owner")


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


class Assembly(Base):
    __tablename__ = "assemblies"

    id = Column(Integer, primary_key=True, index=True)
    userid = Column(String, ForeignKey("users.id"))  # Связь с пользователем
    
    cpu = Column(String)
    artcpu = Column(Integer, unique=True)
    gpu = Column(String)
    artgpu = Column(Integer, unique=True)
    motherboard = Column(String)
    artmotherboard = Column(Integer, unique=True)
    ram = Column(String)
    artram = Column(Integer, unique=True)
    storage = Column(String)
    artstorage = Column(Integer, unique=True)
    case = Column(String)
    artcase = Column(Integer, unique=True)
    cpucool = Column(String)
    artcpucool = Column(Integer, unique=True)
    psu = Column(String)
    artpsu = Column(Integer, unique=True)
    
    owner = relationship("User", back_populates="assemblies")


class AIChatHistory(Base):
    __tablename__ = "ai_chat_history"

    id = Column(Integer, primary_key=True, index=True)
    prompt = Column(String, index=True) 
    response = Column(String, index=True) 
    timestamp = Column(String, index=True)
    
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="chat_history")
