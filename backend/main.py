from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from ai_service import handle_ai_request  # Импортируем функцию для работы с ИИ
from schemas import (
    AIRequest,
    UserCreate,
    Token,
    UserOut,
    UserLogin,
    ComponentOut,
)  # Импортируем нужные схемы
from models import Component
from auth_service import (
    register_user,
    authenticate_user,
    create_access_token,
    get_current_user,
)
from db import engine, Base, get_db
from fastapi.middleware.cors import CORSMiddleware


Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
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


@app.post("/ai")
async def ask_ai(request: AIRequest, current_user: UserOut = Depends(get_current_user)):
    response = handle_ai_request(request.prompt)
    return {"answer": response}
