from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from db import engine, Base, get_db
from auth_service import (
    register_user,
    authenticate_user,
    create_access_token,
    get_current_user,
)
from schemas import UserCreate, Token, UserOut, UserLogin, ComponentOut
from models import Component


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
def register(user: UserCreate, db: Session = Depends(get_db)):
    return register_user(db, user)


@app.post("/login", response_model=Token)
def login(form_data: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.email, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Неверные данные")
    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}


@app.get("/me", response_model=UserOut)
def me(current_user: UserOut = Depends(get_current_user)):
    return current_user


@app.get("/user/{userid}/components", response_model=List[ComponentOut])
def get_user_components(
    userid: str, 
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    if current_user.userid != userid:
        raise HTTPException(
            status_code=403, 
            detail="You can only access your own components"
        )
    
    components = db.query(Component).filter(Component.userid == userid).all()
    
    if not components:
        raise HTTPException(
            status_code=404,
            detail="No components found for this user"
        )
    
    return components