from pydantic import BaseModel, EmailStr
import datetime


class UserCreate(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class UserLogin(BaseModel):
    email: str
    password: str


class ComponentOut(BaseModel):
    part: str
    price: int
    type: str
    article_number: int

    class Config:
        from_attributes = True


class AIChatHistory(BaseModel):
    prompt: str
    response: str
    id: int
    user_id: int
    timestamp: str
    
    class Config:
        orm_mode = True


class AIRequestCreate(BaseModel):
    query: str


class AIRequestResponse(BaseModel):
    id: int
    query: str
    response: str
    timestamp: datetime.datetime

    class Config:
        from_attributes = True
