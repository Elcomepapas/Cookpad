from sqlalchemy.orm import Session

from src.dtos.auth_dto import LoginDTO, TokenDTO
from src.mappers.user_mapper import to_user_response
from src.repositories.user_repository import UserRepository
from src.utils.errors import UnauthorizedError
from src.utils.hash import verify_password
from src.utils.jwt import create_access_token


class AuthService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def login(self, dto: LoginDTO) -> TokenDTO:
        user = self.repo.find_by_email(dto.email)
        if not user or not user.password_hash or not verify_password(dto.password, user.password_hash):
            raise UnauthorizedError("Invalid credentials")

        token = create_access_token({"sub": str(user.id), "email": user.email})
        return TokenDTO(access_token=token, usuario=to_user_response(user))
