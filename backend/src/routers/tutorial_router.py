from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from src.db.connection import get_db
from src.db.models.usuario_model import User
from src.dtos.tutorial_dto import (
    CategoriaTutorial,
    CreateTutorialDTO,
    TutorialResponseDTO,
)
from src.middlewares.auth_middleware import get_current_admin
from src.schemas.tutorial_schema import CreateTutorialSchema
from src.services.tutorial_service import TutorialService

router = APIRouter(tags=["tutoriales"])


@router.post(
    "/tutoriales",
    response_model=TutorialResponseDTO,
    status_code=status.HTTP_201_CREATED,
)
def create_tutorial(
    payload: CreateTutorialSchema,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    dto = CreateTutorialDTO(**payload.model_dump(mode="json"))
    return TutorialService(db).create(dto)


@router.get("/tutoriales", response_model=list[TutorialResponseDTO])
def list_tutorials(
    categoria: CategoriaTutorial | None = None,
    query: Annotated[
        str | None, Query(alias="q", max_length=200, description="Buscar en el título")
    ] = None,
    db: Session = Depends(get_db),
):
    return TutorialService(db).list_all(categoria, query)


@router.get("/tutoriales/{tutorial_id}", response_model=TutorialResponseDTO)
def get_tutorial(tutorial_id: int, db: Session = Depends(get_db)):
    return TutorialService(db).get_by_id(tutorial_id)


@router.get(
    "/recetas/{recipe_id}/tutoriales", response_model=list[TutorialResponseDTO]
)
def list_recipe_tutorials(recipe_id: int, db: Session = Depends(get_db)):
    return TutorialService(db).list_for_recipe(recipe_id)
