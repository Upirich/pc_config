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


class AIHistory(BaseModel):
    id: int
    user_id: int
    request_text: str
    response_text: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True


class AIRequestCreate(BaseModel):
    query: str


class AIRequestResponse(BaseModel):
    id: int
    query: str
    response: str
    timestamp: datetime.datetime

    class Config:
        from_attributes = True


class ComponentOut(BaseModel):
    part: str
    price: int
    type: str
    article_number: int
    description: str | None = None  # <-- добавлено

    class Config:
        from_attributes = True
