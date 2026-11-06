from src.db.models.usuario_model import User
from src.dtos.user_dto import UserResponseDTO


def to_user_response(user: User) -> UserResponseDTO:
    """Convierte un Model SQLAlchemy en un DTO de respuesta (sin campos sensibles)."""
    return UserResponseDTO.model_validate(user)
