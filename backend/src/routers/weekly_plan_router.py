from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from src.db.connection import get_db
from src.db.models.usuario_model import User
from src.dtos.weekly_plan_dto import ShoppingListItemDTO, WeeklyPlanResponseDTO
from src.middlewares.auth_middleware import get_current_user
from src.schemas.weekly_plan_schema import (
    AddPlanRecipeSchema,
    CreateWeeklyPlanSchema,
)
from src.services.weekly_plan_service import WeeklyPlanService

router = APIRouter(prefix="/planes", tags=["planes"])


@router.post(
    "",
    response_model=WeeklyPlanResponseDTO,
    status_code=status.HTTP_201_CREATED,
)
def create_weekly_plan(
    payload: CreateWeeklyPlanSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return WeeklyPlanService(db).create(current_user.id, payload.fecha_inicio)


@router.get("/{plan_id}", response_model=WeeklyPlanResponseDTO)
def get_weekly_plan(
    plan_id: int = Path(gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return WeeklyPlanService(db).get(current_user.id, plan_id)


@router.get(
    "/{plan_id}/lista-compras",
    response_model=list[ShoppingListItemDTO],
)
def get_shopping_list(
    plan_id: int = Path(gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return WeeklyPlanService(db).shopping_list(current_user.id, plan_id)


@router.post(
    "/{plan_id}/recetas",
    response_model=WeeklyPlanResponseDTO,
    status_code=status.HTTP_201_CREATED,
)
def add_recipe_to_plan(
    payload: AddPlanRecipeSchema,
    plan_id: int = Path(gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return WeeklyPlanService(db).add_recipe(
        current_user.id,
        plan_id,
        payload.receta_id,
        payload.dia_semana,
        payload.comida,
        payload.porciones,
    )


@router.delete(
    "/{plan_id}/recetas/{entry_id}",
    response_model=WeeklyPlanResponseDTO,
)
def remove_recipe_from_plan(
    plan_id: int = Path(gt=0),
    entry_id: int = Path(gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return WeeklyPlanService(db).remove_recipe(current_user.id, plan_id, entry_id)
