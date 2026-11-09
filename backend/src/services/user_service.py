from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.dtos.user_dto import CreateUserDTO, UpdateUserDTO, UserResponseDTO
from src.mappers.user_mapper import to_user_response
from src.repositories.user_repository import UserRepository
from src.utils.errors import BadRequestError, ConflictError, NotFoundError
from src.utils.hash import hash_password


class UserService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def create(self, dto: CreateUserDTO) -> UserResponseDTO:
        """Ejemplo completo: hashea la password, crea el user y devuelve el DTO de respuesta."""
        if self.repo.find_by_email(dto.email):
            raise ConflictError("An account with this email already exists")

        password_hash = hash_password(dto.password)
        try:
            user = self.repo.create(
                email=dto.email,
                nombre=dto.nombre,
                password_hash=password_hash,
            )
        except IntegrityError as exc:
            # Handles a duplicate email inserted concurrently after the pre-check.
            raise ConflictError("An account with this email already exists") from exc
        return to_user_response(user)

    def get_by_id(self, user_id: int) -> UserResponseDTO:
        user = self.repo.find_by_id(user_id)
        if user is None:
            raise NotFoundError("User not found")
        return to_user_response(user)

    def list_all(self) -> list[UserResponseDTO]:
        return [to_user_response(user) for user in self.repo.list_all()]

    def update(self, user_id: int, dto: UpdateUserDTO) -> UserResponseDTO:
        if self.repo.find_by_id(user_id) is None:
            raise NotFoundError("User not found")

        fields = {key: value for key, value in dto.model_dump().items() if value is not None}
        if not fields:
            raise BadRequestError("At least one field must be provided")

        email = fields.get("email")
        if email:
            existing = self.repo.find_by_email(email)
            if existing is not None and existing.id != user_id:
                raise ConflictError("An account with this email already exists")

        try:
            user = self.repo.update(user_id, **fields)
        except IntegrityError as exc:
            raise ConflictError("An account with this email already exists") from exc
        if user is None:
            raise NotFoundError("User not found")
        return to_user_response(user)

    def delete(self, user_id: int) -> None:
        if not self.repo.delete(user_id):
            raise NotFoundError("User not found")
