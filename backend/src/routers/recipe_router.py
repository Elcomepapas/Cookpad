from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from src.db.connection import get_db
from src.db.models.usuario_model import User
from src.dtos.recipe_dto import CreateRecipeDTO, RecipeResponseDTO, SearchRecipeDTO
from src.middlewares.auth_middleware import get_current_user
from src.schemas.recipe_schema import CreateRecipeSchema, SearchRecipeSchema
from src.services.recipe_service import RecipeService

router = APIRouter(prefix="/recetas", tags=["recetas"])


@router.get("", response_model=list[RecipeResponseDTO])
@router.get("/", response_model=list[RecipeResponseDTO], include_in_schema=False)
def list_recipes(
    filters: Annotated[SearchRecipeSchema, Query()],
    db: Session = Depends(get_db),
):
    dto = SearchRecipeDTO(**filters.model_dump())
    return RecipeService(db).list_all(dto)


@router.get("/{recipe_id}", response_model=RecipeResponseDTO)
def get_recipe(
    recipe_id: int,
    porciones: int | None = Query(default=None, gt=0),
    db: Session = Depends(get_db),
):
    return RecipeService(db).get_by_id(recipe_id, porciones)


@router.post("/", response_model=RecipeResponseDTO, status_code=status.HTTP_201_CREATED)
def create_recipe(
    payload: CreateRecipeSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    dto = CreateRecipeDTO(**payload.model_dump())
    return RecipeService(db).create(current_user.id, dto)
