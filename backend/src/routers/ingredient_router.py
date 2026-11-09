from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.db.connection import get_db
from src.db.models.usuario_model import User
from src.dtos.ingredient_dto import CreateIngredientDTO, IngredientResponseDTO
from src.middlewares.auth_middleware import get_current_admin
from src.schemas.ingredient_schema import CreateIngredientSchema
from src.services.ingredient_service import IngredientService

router = APIRouter(prefix="/ingredientes", tags=["ingredientes"])


@router.get("/", response_model=list[IngredientResponseDTO])
def list_ingredients(db: Session = Depends(get_db)):
    return IngredientService(db).list_all()


@router.post(
    "/",
    response_model=IngredientResponseDTO,
    status_code=status.HTTP_201_CREATED,
)
def create_ingredient(
    payload: CreateIngredientSchema,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    dto = CreateIngredientDTO(**payload.model_dump())
    return IngredientService(db).create(dto)
