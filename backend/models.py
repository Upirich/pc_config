from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    userid = Column(String, unique=True, index=True)  # Новая колонна для связи
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    # Связь с компонентами
    components = relationship("Component", back_populates="owner")


class Component(Base):
    __tablename__ = "components"

    id = Column(Integer, primary_key=True, index=True)
    userid = Column(String, ForeignKey("users.userid"))  # Внешний ключ
    part = Column(String, unique=False, index=True)
    price = Column(Integer, unique=False, index=True)
    type = Column(String, unique=False, index=True)
    article_number = Column(Integer, unique=True, index=True)

    
    # Связь с пользователем так, чтобы одному прользователю могли принадлежать разные компоненты
    owner = relationship("User", back_populates="components")