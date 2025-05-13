from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from db import get_db
from auth import get_current_user
from schemas.assembly import AssemblyCreate, AssemblyOut
from models import Assembly, User
from crud.assembly import create_assembly, get_user_assemblies

router = APIRouter(
    prefix="/assemblies",
    tags=["assemblies"]
)

# Создание новой сборки (аналогично /register и /components)
@router.post(
    "/",
    response_model=AssemblyOut,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новую сборку",
    response_description="Созданная сборка"
)
def create_new_assembly(
    assembly: AssemblyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Создает новую сборку комплектующих для текущего пользователя.
    
    - **cpu**: Процессор (обязательно)
    - **artcpu**: Артикул процессора (обязательно, уникальный)
    - **gpu**: Видеокарта (опционально)
    - **artgpu**: Артикул видеокарты (опционально, уникальный)
    - ... (остальные поля)
    """
    try:
        return create_assembly(db=db, assembly=assembly, userid=current_user.userid)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# Получение всех сборок пользователя (аналогично /me и /user/{userid}/components)
@router.get(
    "/",
    response_model=List[AssemblyOut],
    summary="Получить все сборки пользователя",
    response_description="Список сборок"
)
def get_assemblies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получает все сборки, принадлежащие текущему авторизованному пользователю.
    
    Возвращает список сборок с комплектующими.
    """
    assemblies = get_user_assemblies(db, userid=current_user.userid)
    if not assemblies:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сборки не найдены"
        )
    return assemblies