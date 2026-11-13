from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.db.connection import get_db
from src.dtos.tutorial_dto import CategoriaTutorial, TutorialResponseDTO
from src.services.tutorial_service import TutorialService

router = APIRouter(tags=["tutoriales"])


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
