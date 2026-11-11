from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from src.db.connection import get_db
from src.db.models.usuario_model import User
from src.dtos.comment_dto import CommentDTO, CommentResponseDTO
from src.middlewares.auth_middleware import get_current_user
from src.schemas.comment_schema import CommentSchema
from src.services.comment_service import CommentService

router = APIRouter(prefix="/recetas", tags=["comentarios"])


@router.post("/{recipe_id}/comentarios", response_model=CommentResponseDTO,
             status_code=status.HTTP_201_CREATED)
def create_comment(
    payload: CommentSchema,
    recipe_id: int = Path(gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    dto = CommentDTO(**payload.model_dump())
    return CommentService(db).create(current_user.id, recipe_id, dto)


@router.put("/{recipe_id}/comentarios/{comment_id}", response_model=CommentResponseDTO)
def update_comment(
    payload: CommentSchema,
    recipe_id: int = Path(gt=0),
    comment_id: int = Path(gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    dto = CommentDTO(**payload.model_dump())
    return CommentService(db).update(current_user.id, recipe_id, comment_id, dto)


@router.get("/{recipe_id}/comentarios", response_model=list[CommentResponseDTO])
def list_comments(
    recipe_id: int = Path(gt=0),
    db: Session = Depends(get_db),
):
    return CommentService(db).list_by_recipe(recipe_id)
