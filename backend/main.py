from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ai_service import handle_ai_request
from schemas import (
    UserCreate,
    Token,
    UserOut,
    UserLogin,
    ComponentOut,
    AIHistory,
    AIRequestCreate,
    AIRequestResponse,
)
from models import Component, AIRequestChat
from fastapi.middleware.cors import CORSMiddleware
from db import engine, Base, get_db
from auth_service import (
    register_user,
    authenticate_user,
    create_access_token,
    get_current_user,
)
import datetime


Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/register", response_model=UserOut)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    return register_user(db, user)


@app.post("/login", response_model=Token)
async def login(form_data: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.email, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Неверные данные")
    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}


@app.get("/me", response_model=UserOut)
async def me(current_user: UserOut = Depends(get_current_user)):
    return current_user


@app.get("/components", response_model=list[ComponentOut])
async def get_user_components(
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user),
):
    components = db.query(Component).filter(Component.userid == current_user.id).all()

    if not components:
        raise HTTPException(status_code=404, detail="No components found for this user")

    return components


@app.post("/ai", response_model=AIRequestResponse)
async def create_ai_request(
    request: AIRequestCreate,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user),
):
    ai_response = handle_ai_request(request.query)

    db_request = AIRequestChat(
        user_id=current_user.id,
        request_text=request.query,
        response_text=ai_response,
        created_at=datetime.datetime.now(),
    )
    db.add(db_request)
    db.commit()
    db.refresh(db_request)

    return {
        "id": current_user.id,
        "query": request.query,
        "response": ai_response,
        "timestamp": datetime.datetime.now(),
    }


@app.get("/history", response_model=list[AIHistory])
async def get_ai_history(
    db: Session = Depends(get_db), current_user: UserOut = Depends(get_current_user)
):
    requests = (
        db.query(AIRequestChat)
        .filter(AIRequestChat.user_id == current_user.id)
        .order_by(AIRequestChat.created_at.desc())
        .limit(100)
        .all()
    )

    return requests
