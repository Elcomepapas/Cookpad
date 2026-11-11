from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from src.db.connection import get_db
from src.db.models.usuario_model import User
from src.dtos.saved_recipe_dto import (
    SaveRecipeDTO, SavedRecipeDetailsDTO, SavedRecipeResponseDTO,
)
from src.middlewares.auth_middleware import get_current_user
from src.schemas.saved_recipe_schema import SaveRecipeSchema
from src.services.saved_recipe_service import SavedRecipeService
from src.utils.errors import ForbiddenError

router = APIRouter(prefix="/usuarios", tags=["guardadas"])


@router.post("/{user_id}/guardadas", response_model=SavedRecipeResponseDTO,
             status_code=status.HTTP_201_CREATED)
def save_recipe(
    payload: SaveRecipeSchema,
    user_id: int = Path(gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if user_id != current_user.id:
        raise ForbiddenError("You can only manage your own saved recipes")
    dto = SaveRecipeDTO(**payload.model_dump())
    return SavedRecipeService(db).save(current_user.id, dto)


@router.get("/{user_id}/guardadas", response_model=list[SavedRecipeDetailsDTO])
def list_saved_recipes(
    user_id: int = Path(gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if user_id != current_user.id:
        raise ForbiddenError("You can only access your own saved recipes")
    return SavedRecipeService(db).list_saved(current_user.id)
