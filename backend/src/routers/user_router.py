from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from src.db.connection import get_db
from src.db.models.usuario_model import User
from src.dtos.user_dto import CreateUserDTO, UpdateUserDTO, UserResponseDTO
from src.middlewares.auth_middleware import get_current_user
from src.schemas.user_schema import CreateUserSchema, UpdateUserSchema
from src.services.user_service import UserService
from src.utils.errors import ForbiddenError

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponseDTO, status_code=status.HTTP_201_CREATED)
def create_user(payload: CreateUserSchema, db: Session = Depends(get_db)):
    """Ejemplo completo: valida con Schema, arma DTO, llama al service."""
    dto = CreateUserDTO(**payload.model_dump())
    return UserService(db).create(dto)


@router.get("/{user_id}", response_model=UserResponseDTO)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if user_id != current_user.id:
        raise ForbiddenError("You can only access your own account")
    return UserService(db).get_by_id(user_id)


@router.put("/{user_id}", response_model=UserResponseDTO)
def update_user(
    user_id: int,
    payload: UpdateUserSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if user_id != current_user.id:
        raise ForbiddenError("You can only update your own account")
    dto = UpdateUserDTO(**payload.model_dump(exclude_unset=True))
    return UserService(db).update(user_id, dto)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    if user_id != current_user.id:
        raise ForbiddenError("You can only delete your own account")
    UserService(db).delete(user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
