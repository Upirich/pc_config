from pydantic import BaseModel, EmailStr
import datetime
from typing import List


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserOut(BaseModel):
    username: str
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
    id: int
    type: str
    name: str
    price: int
    description: str

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


class BuildCreate(BaseModel):
    name: str
    components: dict


class BuildOut(BaseModel):
    id: int
    name: str
    components: dict
    user_id: int

    class Config:
        from_attributes = True


class Complect(BaseModel):
    id: int
    type: str
    name: str
    price: int
    description: str


class Think(BaseModel):
    explanation: str
    output: str


class FinalAnswer(BaseModel):
    thoughts: List[Think]
    choosen_complect: List[Complect]
    final_answer: str
