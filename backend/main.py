from fastapi import FastAPI, Depends, HTTPException
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
    BuildCreate,
    BuildOut,
)
from models import Component, AIRequestChat, Build
from fastapi.middleware.cors import CORSMiddleware
from db import engine, Base, get_db
from db1 import engine1, Base1, get_db1
from auth_service import (
    register_user,
    authenticate_user,
    create_access_token,
    get_current_user,
)
import datetime

Base.metadata.create_all(bind=engine)
Base1.metadata.create_all(bind=engine1)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://frontend",
        "http://localhost:80",
        "http://localhost:3000",
    ],
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


@app.post("/ai", response_model=AIRequestResponse)
async def create_ai_request(
    request: AIRequestCreate,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user),
):
    try:
        ai_response = handle_ai_request(request.query, current_user.id)

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

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")


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


@app.get("/search_components", response_model=list[ComponentOut])
def search_components(
    query: str,
    db: Session = Depends(get_db1),
):
    search_pattern = f"%{query}%"
    results = db.query(Component).filter(Component.name.ilike(search_pattern)).all()
    if not results:
        raise HTTPException(status_code=404, detail="Ничего не найдено")
    return results


@app.post("/builds", response_model=BuildOut)
async def create_build(
    build: BuildCreate,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user),
):
    valid_types = [
        "cpu",
        "gpu",
        "motherboard",
        "ram",
        "storage",
        "psu",
        "cpucool",
        "case",
    ]
    for component_type in build.components.keys():
        if component_type not in valid_types:
            raise HTTPException(
                status_code=400, detail=f"Invalid component type: {component_type}"
            )

    db_build = Build(
        name=build.name, components=build.components, user_id=current_user.id
    )
    db.add(db_build)
    db.commit()
    db.refresh(db_build)
    return db_build


@app.get("/builds/{build_id}", response_model=BuildOut)
async def get_build(
    build_id: int,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user),
):
    build = (
        db.query(Build)
        .filter(Build.id == build_id, Build.user_id == current_user.id)
        .first()
    )

    if not build:
        raise HTTPException(status_code=404, detail="Build not found")

    return build


@app.get("/userbuilds", response_model=list[BuildOut])
async def get_builds(
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user),
):
    builds = db.query(Build).filter(Build.user_id == current_user.id).limit(20)
    return builds.all()


@app.delete("/builds/{build_id}")
async def delete_build(
    build_id: int,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user),
):
    db_build = (
        db.query(Build)
        .filter(Build.id == build_id, Build.user_id == current_user.id)
        .first()
    )

    if not db_build:
        raise HTTPException(status_code=404, detail="Build not found")

    db.delete(db_build)
    db.commit()

    return {"status": "success", "message": "Build deleted"}
